# Policies checked against every Terraform plan with conftest.
#   terraform show -json plan.out > plan.json && conftest test plan.json --policy policy/
package main

import rego.v1   # v1 syntax on older OPA/conftest versions; a no-op on OPA 1.x

deny contains msg if {
	some rc in input.resource_changes
	rc.type == "aws_s3_bucket_public_access_block"
	rc.change.after.block_public_policy != true
	msg := sprintf("%s must block public bucket policies", [rc.address])
}

# Legacy security group rule resource
deny contains msg if {
	some rc in input.resource_changes
	rc.type == "aws_security_group_rule"
	rc.change.after.type == "ingress"
	"0.0.0.0/0" in rc.change.after.cidr_blocks
	rc.change.after.from_port <= 22
	rc.change.after.to_port >= 22
	msg := sprintf("%s opens SSH to the internet", [rc.address])
}

# Current security group rule resource (AWS provider 5+)
deny contains msg if {
	some rc in input.resource_changes
	rc.type == "aws_vpc_security_group_ingress_rule"
	rc.change.after.cidr_ipv4 == "0.0.0.0/0"
	rc.change.after.from_port <= 22
	rc.change.after.to_port >= 22
	msg := sprintf("%s opens SSH to the internet", [rc.address])
}

# Every taggable resource we create must say who owns it.
warn contains msg if {
	some rc in input.resource_changes
	"create" in rc.change.actions
	tags := object.get(rc.change.after, "tags", null)
	is_object(tags)
	not tags.owner
	msg := sprintf("%s has no owner tag", [rc.address])
}
