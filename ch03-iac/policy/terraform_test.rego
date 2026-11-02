# Unit tests for the policies:  opa test policy/ -v   (or: conftest verify --policy policy/)
package main

import rego.v1

pab(value) := {"resource_changes": [{
	"address": "aws_s3_bucket_public_access_block.this",
	"type": "aws_s3_bucket_public_access_block",
	"change": {"actions": ["create"], "after": {"block_public_policy": value}},
}]}

ssh_rule(cidr, from, to) := {"resource_changes": [{
	"address": "aws_vpc_security_group_ingress_rule.ssh",
	"type": "aws_vpc_security_group_ingress_rule",
	"change": {"actions": ["create"], "after": {"cidr_ipv4": cidr, "from_port": from, "to_port": to}},
}]}

test_public_bucket_policy_is_denied if {
	count(deny) == 1 with input as pab(false)
}

test_blocked_public_policy_is_allowed if {
	count(deny) == 0 with input as pab(true)
}

test_ssh_from_internet_is_denied if {
	count(deny) == 1 with input as ssh_rule("0.0.0.0/0", 22, 22)
}

test_port_range_including_ssh_is_denied if {
	count(deny) == 1 with input as ssh_rule("0.0.0.0/0", 0, 65535)
}

test_ssh_from_office_range_is_allowed if {
	count(deny) == 0 with input as ssh_rule("10.24.0.0/20", 22, 22)
}

test_https_from_internet_is_allowed if {
	count(deny) == 0 with input as ssh_rule("0.0.0.0/0", 443, 443)
}

test_missing_owner_tag_warns if {
	count(warn) == 1 with input as {"resource_changes": [{
		"address": "aws_s3_bucket.this",
		"type": "aws_s3_bucket",
		"change": {"actions": ["create"], "after": {"tags": {"environment": "prod"}}},
	}]}
}
