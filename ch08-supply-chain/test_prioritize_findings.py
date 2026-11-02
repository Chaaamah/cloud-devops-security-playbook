import json

from prioritize_findings import load_epss, load_findings, load_kev, prioritize


def write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content if isinstance(content, str) else json.dumps(content))
    return str(p)


def match(vuln_id, severity, pkg, fix=None, related=None):
    m = {"vulnerability": {"id": vuln_id, "severity": severity,
                           "fix": {"versions": fix or [], "state": "fixed" if fix else "not-fixed"}},
         "artifact": {"name": pkg, "version": "1.0.0"}}
    if related:
        m["relatedVulnerabilities"] = [{"id": related}]
    return m


def test_ranking_follows_kev_then_epss_then_severity(tmp_path):
    findings = write(tmp_path, "findings.json", {"matches": [
        match("CVE-2024-0001", "Critical", "libcrit", fix=["1.0.1"]),        # severe, but unlikely
        match("CVE-2024-0002", "Medium", "libkev", fix=["1.0.2"]),           # exploited in the wild
        match("GHSA-xxxx-yyyy-zzzz", "High", "libghsa", fix=["2.0.0"], related="CVE-2024-0003"),
        match("CVE-2024-0004", "Low", "liblow"),
        match("CVE-2024-0004", "Low", "liblow"),                             # duplicate row
    ]})
    kev = write(tmp_path, "kev.json", {"vulnerabilities": [{"cveID": "CVE-2024-0002"}]})
    epss = write(tmp_path, "epss.csv",
                 "#model_version:v2025.03.14,score_date:2026-11-01T00:00:00+0000\n"
                 "cve,epss,percentile\n"
                 "CVE-2024-0001,0.00100,0.30\n"
                 "CVE-2024-0003,0.45000,0.99\n"
                 "CVE-2024-0004,0.00050,0.10\n")

    ranked = prioritize(load_findings(findings), load_kev(kev), load_epss(epss))

    assert [x.cve for x in ranked] == ["CVE-2024-0002", "CVE-2024-0003", "CVE-2024-0001", "CVE-2024-0004"]
    assert [x.bucket for x in ranked] == ["FIX NOW", "FIX NOW", "PLAN", "WATCH"]


def test_high_epss_without_a_fix_is_not_fix_now(tmp_path):
    findings = write(tmp_path, "f.json", {"matches": [match("CVE-2024-0009", "Medium", "lib")]})
    kev = write(tmp_path, "k.json", {"vulnerabilities": []})
    epss = write(tmp_path, "e.csv", "cve,epss,percentile\nCVE-2024-0009,0.9,0.99\n")
    ranked = prioritize(load_findings(findings), load_kev(kev), load_epss(epss))
    assert ranked[0].bucket == "WATCH"     # nothing to upgrade to yet: mitigate and monitor instead
