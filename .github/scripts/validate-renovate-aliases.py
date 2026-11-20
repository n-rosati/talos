#!/usr/bin/env python3

import json5
import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HELM_REPOS_DIR = REPO_ROOT / "repositories/helm"
RENOVATE_CONFIG = REPO_ROOT / ".github/renovate/kinds.json5"

# Extract HelmRepository names and URLs.
expected = {}

for file in HELM_REPOS_DIR.glob("*.yaml"):
    with file.open() as f:
        for resource in yaml.safe_load_all(f):
            if not isinstance(resource, dict):
                continue

            if resource.get("kind") != "HelmRepository":
                continue

            name = resource["metadata"]["name"]
            url = resource["spec"]["url"]

            if name in expected and expected[name] != url:
                raise ValueError(f"Duplicate HelmRepository: {name}")

            expected[name] = url

# Read Renovate configuration.
with RENOVATE_CONFIG.open() as f:
    config = json5.load(f)

actual = config.get("flux", {}).get("registryAliases", {})

# Compare both mappings.
missing = {k: v for k, v in expected.items() if actual.get(k) != v}
extra = {k: v for k, v in actual.items() if k not in expected}

if missing or extra:
    print("Renovate registryAliases are out of sync.")

    if missing:
        print("\nMissing or incorrect aliases:")
        for name, url in missing.items():
            print(f"  {name}: {url}")

    if extra:
        print("\nAliases without a HelmRepository:")
        for name, url in extra.items():
            print(f"  {name}: {url}")

    raise SystemExit(1)

print(f"Renovate aliases verified: {len(expected)} repositories.")
