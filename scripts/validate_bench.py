#!/usr/bin/env python3
"""Validate a skill's evals/ benchmark contract for skill-evolve.

Usage: validate_bench.py <evals-dir>

Checks ONLY structural / count hard-constraints (see BENCHMARK_STANDARD.md).
Content quality (scenario representativeness, rubric anchoring) is a human
Phase-0 responsibility and is intentionally NOT auto-checked.

Exit: 0 if valid:true, 1 if valid:false (errors[] populated), 2 on argv/IO error.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REQUIRED_FILES = [
    "scenarios.md",
    "rubric.md",
    "invariants.md",
    "posture_probes.md",
    "directional_probes.md",
]
REQUIRED_CONTROLS = [
    "ctrl-A-identity.md",
    "ctrl-B-posture-bad.md",
    "ctrl-C-obvious-regress.md",
]

SCENARIO_RE = re.compile(r"^##\s+scenario-(\d+)-(pos|adv|over)[:\s]", re.MULTILINE)
WEIGHT_RE = re.compile(r"weight:\s*([0-9.]+)", re.IGNORECASE)
INVARIANT_RE = re.compile(r"^[-*]\s+(MUST(?:\s+NOT)?\b|MAY\b|SHOULD(?:\s+NOT)?\b)", re.MULTILINE)
PROBE_RE = re.compile(r"^##\s+directional-probe-(\d+)[:\s]", re.MULTILINE)


def main() -> None:
    if len(sys.argv) != 2:
        print(json.dumps({"valid": False, "errors": ["usage: validate_bench.py <evals-dir>"]}))
        sys.exit(2)
    root = Path(sys.argv[1])
    errors: list[str] = []
    report: dict = {
        "valid": False,
        "evals_dir": str(root),
        "scenarios_total": 0,
        "partition": {"positive": 0, "adversarial": 0, "over_application": 0},
        "criteria_count": 0,
        "criteria_weight_sum": 0.0,
        "invariants_count": 0,
        "directional_probes_count": 0,
        "controls_present": [],
        "errors": errors,
    }

    if not root.is_dir():
        errors.append(f"evals dir not found: {root}")
        print(json.dumps(report, indent=2))
        sys.exit(2)

    for name in REQUIRED_FILES:
        if not (root / name).is_file():
            errors.append(f"missing required file: {name}")

    controls_dir = root / "controls"
    if not controls_dir.is_dir():
        errors.append("missing required directory: controls/")
    else:
        for name in REQUIRED_CONTROLS:
            if (controls_dir / name).is_file():
                report["controls_present"].append(name)
            else:
                errors.append(f"missing required control: controls/{name}")

    if (root / "scenarios.md").is_file():
        matches = SCENARIO_RE.findall((root / "scenarios.md").read_text())
        report["scenarios_total"] = len(matches)
        for _, kind in matches:
            key = {"pos": "positive", "adv": "adversarial", "over": "over_application"}[kind]
            report["partition"][key] += 1
        if len(matches) < 6:
            errors.append(f"scenarios.md must have >= 6 scenarios; found {len(matches)}")
        if report["partition"]["positive"] < 4:
            errors.append(f"need >= 4 positive scenarios; found {report['partition']['positive']}")
        if report["partition"]["adversarial"] < 1:
            errors.append("need >= 1 adversarial (adv) scenario; found 0")
        if report["partition"]["over_application"] < 1:
            errors.append("need >= 1 over-application (over) scenario; found 0")

    if (root / "rubric.md").is_file():
        weights = []
        for raw in WEIGHT_RE.findall((root / "rubric.md").read_text()):
            try:
                weights.append(float(raw))
            except ValueError:
                errors.append(f"rubric.md: malformed weight {raw!r}")
        report["criteria_count"] = len(weights)
        report["criteria_weight_sum"] = round(sum(weights), 4)
        if len(weights) < 3:
            errors.append(f"rubric.md needs >= 3 criteria; found {len(weights)}")
        if weights and not (0.99 <= sum(weights) <= 1.01):
            errors.append(f"rubric.md weights must sum to 1.0 +/- 0.01; found {sum(weights):.3f}")

    if (root / "invariants.md").is_file():
        bullets = INVARIANT_RE.findall((root / "invariants.md").read_text())
        report["invariants_count"] = len(bullets)
        if len(bullets) < 3:
            errors.append(f"invariants.md needs >= 3 RFC-2119 bullets; found {len(bullets)}")

    if (root / "directional_probes.md").is_file():
        probes = PROBE_RE.findall((root / "directional_probes.md").read_text())
        report["directional_probes_count"] = len(probes)
        if len(probes) < 2:
            errors.append(f"directional_probes.md needs >= 2 probes; found {len(probes)}")

    report["valid"] = len(errors) == 0
    print(json.dumps(report, indent=2))
    sys.exit(0 if report["valid"] else 1)


if __name__ == "__main__":
    main()
