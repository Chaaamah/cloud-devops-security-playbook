"""Chapter 8.2: rank vulnerability findings the way an attacker would.

Reads a grype JSON report and enriches each finding with:
  - CISA Known Exploited Vulnerabilities (KEV) catalog: exploited in the wild?
  - FIRST EPSS scores: probability of exploitation in the next 30 days
and sorts them into three buckets: FIX NOW, PLAN, WATCH.

usage:
  grype sbom:sbom.cdx.json -o json > findings.json
  curl -sSLO https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json
  curl -sSL https://epss.cyentia.com/epss_scores-current.csv.gz | gunzip > epss.csv
  python prioritize_findings.py findings.json known_exploited_vulnerabilities.json epss.csv
"""
import csv
import json
import sys
from dataclasses import dataclass

SEVERITY_ORDER = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1, "Negligible": 0, "Unknown": 0}
EPSS_FIX_NOW = 0.10      # 10% chance of exploitation in 30 days is very high in practice


@dataclass
class Finding:
    cve: str
    package: str
    version: str
    severity: str
    fixed_in: str
    in_kev: bool = False
    epss: float = 0.0

    @property
    def bucket(self) -> str:
        if self.in_kev or (self.epss >= EPSS_FIX_NOW and self.fixed_in):
            return "FIX NOW"
        if SEVERITY_ORDER.get(self.severity, 0) >= 3:
            return "PLAN"
        return "WATCH"

    @property
    def sort_key(self):
        return (-int(self.in_kev), -self.epss, -SEVERITY_ORDER.get(self.severity, 0), self.cve)


def cve_of(match: dict) -> str:
    """grype may report a GHSA id; the related CVE is what KEV and EPSS use."""
    vuln_id = match["vulnerability"]["id"]
    if vuln_id.startswith("CVE-"):
        return vuln_id
    for related in match.get("relatedVulnerabilities", []):
        if related.get("id", "").startswith("CVE-"):
            return related["id"]
    return vuln_id


def load_findings(path: str) -> list[Finding]:
    with open(path) as f:
        report = json.load(f)
    seen, findings = set(), []
    for m in report.get("matches", []):
        key = (cve_of(m), m["artifact"]["name"], m["artifact"]["version"])
        if key in seen:
            continue
        seen.add(key)
        fix = m["vulnerability"].get("fix", {})
        findings.append(Finding(
            cve=key[0], package=key[1], version=key[2],
            severity=m["vulnerability"].get("severity", "Unknown"),
            fixed_in=", ".join(fix.get("versions", [])),
        ))
    return findings


def load_kev(path: str) -> set[str]:
    with open(path) as f:
        return {v["cveID"] for v in json.load(f)["vulnerabilities"]}


def load_epss(path: str) -> dict[str, float]:
    with open(path) as f:
        rows = (line for line in f if not line.startswith("#"))   # first line is model metadata
        return {r["cve"]: float(r["epss"]) for r in csv.DictReader(rows)}


def prioritize(findings: list[Finding], kev: set[str], epss: dict[str, float]) -> list[Finding]:
    for item in findings:
        item.in_kev = item.cve in kev
        item.epss = epss.get(item.cve, 0.0)
    return sorted(findings, key=lambda x: x.sort_key)


def main() -> None:
    findings_path, kev_path, epss_path = sys.argv[1:4]
    ranked = prioritize(load_findings(findings_path), load_kev(kev_path), load_epss(epss_path))
    print(f"{'BUCKET':<8} {'CVE':<16} {'KEV':<4} {'EPSS':>6} {'SEVERITY':<9} PACKAGE (FIX)")
    for x in ranked:
        print(f"{x.bucket:<8} {x.cve:<16} {'yes' if x.in_kev else '':<4} {x.epss:6.3f} "
              f"{x.severity:<9} {x.package} {x.version} ({x.fixed_in or 'no fix yet'})")
    counts = {b: sum(1 for x in ranked if x.bucket == b) for b in ("FIX NOW", "PLAN", "WATCH")}
    print(f"\n{len(ranked)} findings: " + ", ".join(f"{n} {b}" for b, n in counts.items()))


if __name__ == "__main__":
    main()
