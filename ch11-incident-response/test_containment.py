"""Unit tests with fake AWS clients: no credentials, no cloud calls."""
import datetime as dt
import json
import sys
from unittest.mock import MagicMock

sys.modules.setdefault("boto3", MagicMock())     # tests run even where boto3 is not installed

from contain_instance import contain_instance          # noqa: E402
from revoke_role_sessions import revoke_sessions       # noqa: E402


def fake_ec2():
    ec2 = MagicMock()
    ec2.describe_instances.return_value = {"Reservations": [{"Instances": [{
        "SecurityGroups": [{"GroupId": "sg-app"}, {"GroupId": "sg-ssh"}],
        "BlockDeviceMappings": [{"Ebs": {"VolumeId": "vol-1"}}, {"Ebs": {"VolumeId": "vol-2"}}],
    }]}]}
    ec2.create_snapshot.side_effect = [{"SnapshotId": "snap-1"}, {"SnapshotId": "snap-2"}]
    return ec2


def test_evidence_is_preserved_before_isolation():
    ec2 = fake_ec2()
    result = contain_instance(ec2, "i-123", "sg-quarantine", "IR-42")

    names = [c[0] for c in ec2.method_calls]
    assert names.index("create_snapshot") < names.index("modify_instance_attribute")
    assert result["snapshots"] == ["snap-1", "snap-2"]

    calls = ec2.modify_instance_attribute.call_args_list
    assert calls[0].kwargs == {"InstanceId": "i-123", "DisableApiTermination": {"Value": True}}
    assert calls[1].kwargs == {"InstanceId": "i-123", "Groups": ["sg-quarantine"]}


def test_original_security_groups_are_recorded_for_recovery():
    ec2 = fake_ec2()
    contain_instance(ec2, "i-123", "sg-quarantine", "IR-42")
    tags = {t["Key"]: t["Value"] for t in ec2.create_tags.call_args.kwargs["Tags"]}
    assert tags["original-security-groups"] == "sg-app,sg-ssh"
    assert tags["case"] == "IR-42" and tags["status"] == "quarantined"


def test_revocation_denies_sessions_issued_before_the_cutoff():
    iam = MagicMock()
    cutoff = dt.datetime(2026, 3, 12, 14, 30, tzinfo=dt.timezone.utc)
    revoke_sessions(iam, "checkout-deploy", cutoff)

    doc = json.loads(iam.put_role_policy.call_args.kwargs["PolicyDocument"])
    statement = doc["Statement"][0]
    assert statement["Effect"] == "Deny" and statement["Action"] == "*"
    assert statement["Condition"] == {"DateLessThan": {"aws:TokenIssueTime": "2026-03-12T14:30:00Z"}}
