"""Contain a compromised EC2 instance while preserving evidence.

usage: python contain_instance.py <instance-id> <quarantine-sg-id> <case-id> [--region eu-west-1]
"""
import argparse
import datetime as dt

import boto3


def contain_instance(ec2, instance_id: str, quarantine_sg: str, case_id: str) -> dict:
    reservation = ec2.describe_instances(InstanceIds=[instance_id])["Reservations"][0]
    instance = reservation["Instances"][0]
    original_sgs = [g["GroupId"] for g in instance["SecurityGroups"]]

    # 1. Snapshot every attached volume before anything changes.
    snapshots = []
    for mapping in instance.get("BlockDeviceMappings", []):
        volume_id = mapping["Ebs"]["VolumeId"]
        snap = ec2.create_snapshot(
            VolumeId=volume_id,
            Description=f"{case_id} evidence {instance_id} {volume_id}",
            TagSpecifications=[{
                "ResourceType": "snapshot",
                "Tags": [{"Key": "case", "Value": case_id}],
            }],
        )
        snapshots.append(snap["SnapshotId"])

    # 2. Prevent termination, which would destroy disks and memory.
    ec2.modify_instance_attribute(InstanceId=instance_id,
                                  DisableApiTermination={"Value": True})

    # 3. Isolate: replace all security groups with the quarantine group.
    ec2.modify_instance_attribute(InstanceId=instance_id, Groups=[quarantine_sg])

    # 4. Record what changed, for the case file and for recovery.
    ec2.create_tags(Resources=[instance_id], Tags=[
        {"Key": "case", "Value": case_id},
        {"Key": "status", "Value": "quarantined"},
        {"Key": "original-security-groups", "Value": ",".join(original_sgs)},
        {"Key": "quarantined-at", "Value": dt.datetime.now(dt.timezone.utc).isoformat()},
    ])
    return {"snapshots": snapshots, "original_security_groups": original_sgs}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("instance_id")
    p.add_argument("quarantine_sg")
    p.add_argument("case_id")
    p.add_argument("--region", default="eu-west-1")
    a = p.parse_args()
    result = contain_instance(boto3.client("ec2", region_name=a.region),
                              a.instance_id, a.quarantine_sg, a.case_id)
    print(f"Quarantined {a.instance_id}; evidence snapshots: {', '.join(result['snapshots'])}")
    print("Next: detach the instance profile, revoke its role sessions (revoke_role_sessions.py),"
          " and apply a deny-all NACL if established connections must be cut.")


if __name__ == "__main__":
    main()
