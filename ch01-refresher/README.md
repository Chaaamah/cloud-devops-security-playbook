# Chapter 1 — The fundamentals refresher

## Self-assessment answers, with the reasoning

1. **59 usable addresses.** A /26 has 2^(32−26) = 64 addresses. AWS reserves 5 in every subnet: the network address, the VPC router, the DNS server, one for future use and the broadcast address.
2. **Security groups vs network ACLs.** Security groups are *stateful* (return traffic is allowed automatically), support allow rules only, and attach to network interfaces. NACLs are *stateless* (you must allow the return traffic, including ephemeral ports), support allow and deny, and attach to subnets.
3. **Namespaces and cgroups.** Namespaces limit what a process sees; cgroups limit what it uses.
4. **`CAP_SYS_ADMIN`** is so broad, covering mounts, namespaces and many device operations, that it is often called "the new root". Many container escapes rely on it.
5. **The provider** patches the engine of a managed database. You remain responsible for its configuration, network exposure, credentials and data.
6. **Envelope encryption.** Data is encrypted locally with a data key; the data key is encrypted by a master key that never leaves the key management service. It keeps encryption fast and limits master-key exposure to small, audited API calls.
7. **`dig +trace`** shows the full delegation path: root servers, then the top-level domain servers, then the authoritative servers.
8. **Overlapping CIDRs** cannot be routed to each other, so VPC peering, Transit Gateway attachments and VPNs between them fail or need complex NAT.
9. **IAM user vs role.** A user has long-term credentials; a role is assumed and issues temporary credentials. Prefer roles everywhere.
10. **Assume breach** shifts design toward limiting blast radius: segmentation, least privilege, short-lived credentials and monitoring of internal traffic, not just the perimeter.

## If you scored below 8

| Gap | Fix it with |
| --- | --- |
| Networking | Build a VPC by hand: two subnets, a NAT gateway, a security group, then trace a packet with `traceroute` and flow logs |
| Linux | Run a container, then inspect its namespaces and capabilities under `/proc/<pid>/` on the host |
| Cloud IAM | Write a policy from scratch that allows reading one S3 prefix only, then test it with the IAM policy simulator |
| Cryptography | Encrypt a file with a KMS data key using envelope encryption, then decrypt it |

## Quick commands from the chapter

```bash
ip route; traceroute example.com          # layer 3
ss -tlnp; nc -vz example.com 443          # layer 4
openssl s_client -connect example.com:443 -servername example.com </dev/null | openssl x509 -noout -dates
curl -v https://example.com; dig +trace example.com
ps -eo pid,user,cmd --forest
grep Cap /proc/<pid>/status | xargs -L1 echo   # then decode with: capsh --decode=<hex>
```
