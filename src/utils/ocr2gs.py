#!/usr/bin/env python3
import argparse
import re
from difflib import SequenceMatcher

# ----------------------------
# Normalization helpers
# ----------------------------

def normalize(s):
    s = s.lower()
    s = re.sub(r"[^\w\s]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def fix_missing_spaces_after_dots(text):
    hits = re.findall(r"\.[A-Za-zÄÖÜäöü]", text)
    if len(hits) > 3:
        text = re.sub(r"\.([A-Za-zÄÖÜäöü])", r". \1", text)
    return text


# ----------------------------
# OCR preprocessing
# ----------------------------

def preprocess_ocr(text, md=False):
    text = text.replace("-", "=")

    if md:
        text = text.replace("#", "\n")

    text = re.sub(r"\n+", "\n", text)
    text = fix_missing_spaces_after_dots(text)
    return text


# ----------------------------
# Core alignment logic
# ----------------------------

def reformat_ocr_to_gs(ocr, gs_lines):
    out = []
    ocr_len = len(ocr)
    ocr_pos = 0

    def next_match(start_pos, target_norm, window=400):
        """
        Find best fuzzy match of target_norm in OCR starting at start_pos.
        Returns (orig_start, orig_end) or None.
        """
        best_ratio = 0
        best_span = None

        buf = ""
        buf_map = []  # maps normalized char index → original index

        for i in range(start_pos, min(ocr_len, start_pos + window)):
            c = ocr[i]
            n = normalize(c)
            if n:
                buf += n
                buf_map.append(i)

            if len(buf) < len(target_norm) // 2:
                continue

            chunk = buf[-len(target_norm) - 10 :]
            ratio = SequenceMatcher(None, target_norm, chunk).ratio()

            if ratio > best_ratio:
                best_ratio = ratio
                end_idx = buf_map[-1]
                start_idx = buf_map[-len(chunk)]
                best_span = (start_idx, end_idx + 1)

        if best_ratio >= 0.55:
            return best_span
        return None

    while gs_lines:
        gs_line = gs_lines.pop(0)
        has_hyphen = gs_line.rstrip().endswith("=")
        gs_text = gs_line.rstrip("=").strip()

        if not gs_text:
            out.append("")
            continue

        gs_norm = normalize(gs_text)

        match = next_match(ocr_pos, gs_norm)
        if not match:
            out.append("")
            continue

        start, end = match

        # Respect word boundaries unless GS hyphenates
        if not has_hyphen:
            while end < ocr_len and not ocr[end].isspace():
                end += 1

        segment = ocr[start:end].strip()

        if has_hyphen and not segment.endswith("="):
            segment += "="

        out.append(segment)
        ocr_pos = end

    return "\n".join(out)

# ----------------------------
# CLI
# ----------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ocr")
    ap.add_argument("gs")
    ap.add_argument("out")
    ap.add_argument("--md", action="store_true")
    args = ap.parse_args()

    with open(args.ocr, encoding="utf-8") as f:
        ocr = f.read()

    with open(args.gs, encoding="utf-8") as f:
        gs_lines = [l.rstrip("\n") for l in f]

    ocr = preprocess_ocr(ocr, args.md)
    result = reformat_ocr_to_gs(ocr, gs_lines)

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(result)


if __name__ == "__main__":
    main()

