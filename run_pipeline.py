#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from typing import List, Sequence

@dataclass(frozen=True)
class Step:
    id: str
    title: str
    cmd: Sequence[str]
    file_to_check: str | None = None  # optional existence check

STEPS: List[Step] = [
    Step("scra", "Scrape PDFs", ["python3", "scra.py"], "scra.py"),
    Step("twopages", "Keep only the usable pages", ["python3", "twopages.py"], "twopages.py"),
    Step("extract_pdf_text", "Extract text from PDFs", ["python3", "extract_pdf-text.py"], "extract_pdf-text.py"),
    Step("reorganize_text_files", "Reorganize text and PDFs by page number", ["python3", "reorganize_text-files.py"], "reorganize_text-files.py"),
    Step("onepage", "Ensure one page per text file", ["bash", "onepage.sh"], "onepage.sh"),
    Step("extract_units", "Extract units", ["python3", "extract_units.py"], "extract_units.py"),
    Step("add_unit_name_prefix", "Add unit name prefix", ["python3", "add_unit_name_prefix.py"], "add_unit_name_prefix.py"),
    Step("categorize_files", "Categorize files", ["python3", "categorize_files.py"], "categorize_files.py"),
    Step("sort_filenames_in_json", "Sort filenames in JSON", ["python3", "sort_filenames_in_json.py"], "sort_filenames_in_json.py"),
    Step("create_hierarchical_categories", "Create hierarchical categories", ["python3", "create_hierarchical_categories.py"], "create_hierarchical_categories.py"),
    Step("group_consecutive_uncategorized", "Group consecutive uncategorized", ["python3", "group_consecutive_uncategorized.py"], "group_consecutive_uncategorized.py"),
    Step("fix_chapter_boundaries", "Fix chapter boundaries", ["python3", "fix_chapter_boundaries.py"], "fix_chapter_boundaries.py"),
]

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def list_steps():
    for i, s in enumerate(STEPS, start=1):
        print(f"{i:2d}. {s.id:28s} - {s.title}")

def resolve_selection(args) -> List[Step]:
    steps = STEPS
    if args.list:
        list_steps()
        sys.exit(0)

    id_to_index = {s.id: i for i, s in enumerate(steps)}
    selected = steps

    if args.only:
        only_ids = [x.strip() for x in args.only.split(",") if x.strip()]
        unknown = [x for x in only_ids if x not in id_to_index]
        if unknown:
            eprint(f"Unknown step id(s): {', '.join(unknown)}")
            list_steps()
            sys.exit(2)
        selected = [steps[id_to_index[x]] for x in only_ids]
    else:
        start = 0
        end = len(steps)
        if args.start:
            if args.start not in id_to_index:
                eprint(f"Unknown --start id: {args.start}")
                list_steps()
                sys.exit(2)
            start = id_to_index[args.start]
        if args.end:
            if args.end not in id_to_index:
                eprint(f"Unknown --end id: {args.end}")
                list_steps()
                sys.exit(2)
            end = id_to_index[args.end] + 1
        selected = steps[start:end]

    if args.skip:
        skip_ids = {x.strip() for x in args.skip.split(",") if x.strip()}
        selected = [s for s in selected if s.id not in skip_ids]

    return selected

def ensure_tools_available():
    required_tools = {"python3": "python3", "bash": "bash"}
    for name, tool in required_tools.items():
        if shutil.which(tool) is None:
            eprint(f"Required tool not found on PATH: {tool}")
            sys.exit(127)

def main():
    parser = argparse.ArgumentParser(description="Run the oo1-extractor pipeline.")
    parser.add_argument("--list", action="store_true", help="List available steps and exit")
    parser.add_argument("--only", help="Comma-separated step ids to run (overrides start/end)")
    parser.add_argument("--start", help="Start from step id (inclusive)")
    parser.add_argument("--end", help="End at step id (inclusive)")
    parser.add_argument("--skip", help="Comma-separated step ids to skip")
    parser.add_argument("--dry-run", action="store_true", help="Print what would run without executing")
    parser.add_argument("--continue-on-error", action="store_true", help="Do not stop on first failing step")
    args = parser.parse_args()

    ensure_tools_available()
    selected = resolve_selection(args)

    if not selected:
        eprint("No steps selected.")
        list_steps()
        return 2

    # Basic repo-root sanity check
    if not os.path.exists("README.md"):
        eprint("Warning: README.md not found in current directory. Are you running from the repo root?")

    print("oo1-extractor pipeline starting")
    print("Selected steps:")
    for s in selected:
        print(f"- {s.id}: {s.title}")

    for s in selected:
        print("\n" + "=" * 80)
        print(f"Step: {s.title} [{s.id}]")
        print("Command:", " ".join(s.cmd))
        if s.file_to_check and not os.path.exists(s.file_to_check):
            eprint(f"Error: required script not found: {s.file_to_check}")
            if not args.continue_on_error:
                return 1
            else:
                continue
        if args.dry_run:
            continue
        try:
            # Use the current environment and inherit stdio
            result = subprocess.run(s.cmd, check=True)
        except subprocess.CalledProcessError as e:
            eprint(f"Step failed ({s.id}) with exit code {e.returncode}")
            if not args.continue_on_error:
                return e.returncode or 1
            else:
                continue

    print("\nPipeline completed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())