#!/usr/bin/env python3
"""
update_pricing.py

Looks in the AWS_pricing_GET_request folder (next to this script) for new
.json files (AWS Price List API "GetProducts" responses, or any file that
contains the pricing "$X.XXXX per On Demand <OS> <instance> Instance Hour"
text somewhere in it). Extracts the six rates this project cares about and
writes them into index.html's RATES table.

Exit codes (used by run_pricing_update.bat to decide whether to run git):
    0 -> index.html was updated, go ahead and commit/push
    2 -> nothing new to process, skip commit/push
    1 -> something went wrong
"""

import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PRICING_DIR = os.path.join(SCRIPT_DIR, "AWS_pricing_GET_request")
INDEX_HTML = os.path.join(SCRIPT_DIR, "index.html")
STATE_FILE = os.path.join(SCRIPT_DIR, ".pricing_state.json")

# Instance types this project tracks (must match the keys in index.html's RATES table)
INSTANCES = ["t3a.large", "t3a.xlarge", "m5.xlarge", "g4ad.xlarge"]
OSES = ["Windows", "Linux"]

# Matches: $0.0752 per On Demand Linux t3a.large Instance Hour
PRICE_RE = re.compile(
    r"\$(\d+(?:\.\d+)?)\s+per\s+On Demand (Windows|Linux) "
    r"(t3a\.large|t3a\.xlarge|m5\.xlarge|g4ad\.xlarge) Instance Hour"
)


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {"processed": []}
    return {"processed": []}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def find_new_json_files(processed):
    if not os.path.isdir(PRICING_DIR):
        print(f"ERROR: pricing directory not found: {PRICING_DIR}")
        sys.exit(1)

    all_json = [
        f for f in os.listdir(PRICING_DIR)
        if f.lower().endswith(".json")
    ]
    new_files = [f for f in all_json if f not in processed]
    # Process in modified-time order, oldest first, so the newest file's
    # prices win if two files disagree.
    new_files.sort(key=lambda f: os.path.getmtime(os.path.join(PRICING_DIR, f)))
    return new_files


def extract_rates(filepath):
    """Read a JSON pricing file as raw text and pull out matching rates."""
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    found = {}
    for match in PRICE_RE.finditer(text):
        price, os_name, instance = match.groups()
        found[(instance, os_name.lower())] = float(price)
    return found


def update_index_html(rates):
    """rates: dict of (instance, 'windows'/'linux') -> float"""
    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    updated_pairs = []

    for instance in INSTANCES:
        line_re = re.compile(
            r"('%s':\s*\{\s*windows:\s*)([\d.]+)(,\s*linux:\s*)([\d.]+)(\s*\},?)"
            % re.escape(instance)
        )

        m = line_re.search(html)
        if not m:
            print(f"WARNING: could not find RATES entry for '{instance}' in index.html")
            continue

        new_windows = rates.get((instance, "windows"))
        new_linux = rates.get((instance, "linux"))

        old_windows = m.group(2)
        old_linux = m.group(4)

        windows_str = _fmt(new_windows) if new_windows is not None else old_windows
        linux_str = _fmt(new_linux) if new_linux is not None else old_linux

        if new_windows is not None and windows_str != old_windows:
            updated_pairs.append(f"{instance} windows: {old_windows} -> {windows_str}")
        if new_linux is not None and linux_str != old_linux:
            updated_pairs.append(f"{instance} linux: {old_linux} -> {linux_str}")

        replacement = m.group(1) + windows_str + m.group(3) + linux_str + m.group(5)
        html = html[: m.start()] + replacement + html[m.end():]

    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    return updated_pairs


def _fmt(value):
    # Keep trailing zeros trimmed but preserve reasonable precision, e.g. 0.0752, 0.224
    s = f"{value:.5f}".rstrip("0")
    if s.endswith("."):
        s += "0"
    return s


def main():
    state = load_state()
    processed = set(state.get("processed", []))

    new_files = find_new_json_files(processed)

    if not new_files:
        print("No new .json files found in AWS_pricing_GET_request. Nothing to do.")
        sys.exit(2)

    print(f"Found {len(new_files)} new file(s): {', '.join(new_files)}")

    combined_rates = {}
    for filename in new_files:
        filepath = os.path.join(PRICING_DIR, filename)
        rates = extract_rates(filepath)
        if not rates:
            print(f"  {filename}: no matching pricing strings found")
        else:
            print(f"  {filename}: found {len(rates)} matching rate(s)")
            combined_rates.update(rates)

    if not combined_rates:
        print("No matching pricing strings found in any new file. index.html not changed.")
        # Still mark these as processed so we don't keep re-scanning junk files.
        state["processed"] = sorted(processed | set(new_files))
        save_state(state)
        sys.exit(2)

    updated_pairs = update_index_html(combined_rates)

    state["processed"] = sorted(processed | set(new_files))
    save_state(state)

    if updated_pairs:
        print("Updated index.html rates:")
        for pair in updated_pairs:
            print(f"  {pair}")
        sys.exit(0)
    else:
        print("Rates found matched existing values in index.html. No changes made.")
        sys.exit(2)


if __name__ == "__main__":
    main()
