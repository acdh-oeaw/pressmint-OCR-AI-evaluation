#!/usr/bin/env python3
import sys
import json
import ast
import argparse
import re

HELP_TEXT = """
dots2txt.py - Extract "text" fields from JSON files

Reads one or more filenames as command-line arguments.

Supported input formats:
  1) Valid JSON list of dicts
  2) Python list containing a single JSON string:
         ['[{"text": "..."}]']
  3) Broken Python list syntax (newlines, spacing, quotes)
  4) Any file that *contains* a JSON list somewhere inside

The script extracts all "text" fields and prints them line by line.
"""


def load_data(content):
    content = content.strip()

    # ---- Try pure JSON ---------------------------------------------------
    try:
        return json.loads(content)
    except Exception:
        pass

    # ---- Try Python literal list containing a JSON string ----------------
    try:
        obj = ast.literal_eval(content)
        if isinstance(obj, list) and len(obj) == 1 and isinstance(obj[0], str):
            return json.loads(obj[0])
    except Exception:
        pass

    # ---- Try extracting JSON array manually ------------------------------
    # Find outermost [...] region
    m = re.search(r'\[.*\]', content, flags=re.DOTALL)
    if m:
        candidate = m.group(0)

        # Try JSON decode directly
        try:
            return json.loads(candidate)
        except Exception:
            pass

        # Try JSON decode after removing outer Python string quotes
        if candidate.startswith("['") and candidate.endswith("']"):
            inner = candidate[2:-2]
            try:
                return json.loads(inner)
            except Exception:
                pass

    raise ValueError("Input does not contain valid JSON data")


def process_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()

        data = load_data(content)

        for item in data:
            if "text" in item:
                print(item["text"])

    except Exception as e:
        print(f"Error processing {filename}: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("files", nargs="*", help="JSON files to process")
    parser.add_argument("-h", "--help", action="store_true")

    args = parser.parse_args()

    if args.help or not args.files:
        print(HELP_TEXT.strip())
        sys.exit(0)

    for filename in args.files:
        process_file(filename)


if __name__ == "__main__":
    main()

