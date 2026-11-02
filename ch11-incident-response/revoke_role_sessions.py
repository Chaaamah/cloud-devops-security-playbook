"""Revoke every session of a role issued before now (temporary credentials stay valid otherwise).

usage: python revoke_role_sessions.py <role-name>
This is what the IAM console's "Revoke active sessions" button does.
"""
import argparse
import datetime as dt
import json

import boto3

POLICY_NAME = "AWSRevokeOlderSessions"


def revoke_policy(cutoff: dt.datetime) -> dict:
    return {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Deny",
            "Action": "*",
            "Resource": "*",
            "Condition": {
                "DateLessThan": {"aws:TokenIssueTime": cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")}
            },
        }],
    }


def revoke_sessions(iam, role_name: str, cutoff: dt.datetime | None = None) -> str:
    cutoff = cutoff or dt.datetime.now(dt.timezone.utc)
    iam.put_role_policy(RoleName=role_name, PolicyName=POLICY_NAME,
                        PolicyDocument=json.dumps(revoke_policy(cutoff)))
    return cutoff.isoformat()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("role_name")
    a = p.parse_args()
    when = revoke_sessions(boto3.client("iam"), a.role_name)
    print(f"Sessions of {a.role_name} issued before {when} are now denied everything.")
    print("Legitimate callers simply assume the role again and get a fresh, valid session.")
