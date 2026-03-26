#!/usr/bin/env python3
"""
OCR to Gold Standard Formatter
Reformats OCR output to match gold standard layout for easier comparison.
Uses hybrid word+character matching to handle word hyphenation.
"""

import sys
import os
from difflib import SequenceMatcher
import re


def clean_ocr_text(text, replace_md_headers=False):
    """Clean OCR text: optionally replace # with newlines if markdown mode."""
    if replace_md_headers:
        # Replace all # characters with newlines (markdown headers)
        text = text.replace('#', '\n')
        # Normalize multiple newlines
        text = re.sub(r'\n+', '\n', text)
    return text


def preprocess_text(text):
    """Add spaces after punctuation if missing."""
    text = re.sub(r'([.!?,;:])([A-Za-z0-9„"])', r'\1 \2', text)
    return text


def normalize_text(text):
    """Normalize text for comparison: lowercase, keep spaces, remove only punctuation."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text


def get_lines(text):
    """Get lines from text, removing empty lines."""
    lines = []
    for line in text.split('\n'):
        stripped = line.strip()
        if stripped:
            lines.append(stripped)
    return lines


def split_word_by_prefix(word, prefix_norm):
    """
    Split a word to match a prefix (accounting for OCR errors).
    Returns (matched_prefix, remainder) or (word, "") if can't split well.
    """
    word_norm = normalize_text(word)
    
    # Try to find best split point
    best_pos = len(prefix_norm)
    best_ratio = 0
    
    # Try positions around the expected length
    for pos in range(max(1, len(prefix_norm) - 3), min(len(word_norm), len(prefix_norm) + 4)):
        prefix_part = word_norm[:pos]
        ratio = SequenceMatcher(None, prefix_norm, prefix_part).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_pos = pos
    
    if best_ratio >= 0.6:  # Good enough match
        # Now split the original word at corresponding position
        # Map normalized position back to original
        norm_count = 0
        for i, c in enumerate(word):
            if not re.match(r'[^\w\s]', c):  # Not punctuation
                norm_count += 1
                if norm_count >= best_pos:
                    return word[:i+1], word[i+1:]
        
        # Fallback
        return word[:best_pos], word[best_pos:]
    else:
        # Can't split well
        return word, ""


def find_nearest_space_before(text, pos):
    """Find the nearest space before position (or start of text)."""
    while pos > 0 and not text[pos-1].isspace():
        pos -= 1
    return pos


def find_nearest_space_after(text, pos):
    """Find the nearest space after position (or end of text)."""
    while pos < len(text) and not text[pos].isspace():
        pos += 1
    return pos


def reformat_ocr_to_gs(ocr_text, gs_text, add_markup=False, replace_md_headers=False):
    """Reformat OCR text to match gold standard layout."""
    
    # Clean and preprocess OCR
    ocr_cleaned = clean_ocr_text(ocr_text, replace_md_headers=replace_md_headers)
    ocr_cleaned = preprocess_text(ocr_cleaned)
    
    # Get lines
    ocr_lines = get_lines(ocr_cleaned)
    gs_lines = get_lines(gs_text)
    
    # Combine into single text
    ocr_combined = ' '.join(ocr_lines)
    gs_combined = ' '.join(gs_lines)
    
    # Normalize for matching
    ocr_normalized = normalize_text(ocr_combined)
    gs_normalized = normalize_text(gs_combined)
    
    # Character-level alignment
    matcher = SequenceMatcher(None, gs_normalized, ocr_normalized)
    
    # Build mapping from GS normalized position to OCR normalized position
    gs_to_ocr = {}
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            for offset in range(i2 - i1):
                gs_to_ocr[i1 + offset] = j1 + offset
        elif tag == 'replace':
            gs_len = i2 - i1
            ocr_len = j2 - j1
            for offset in range(gs_len):
                ocr_offset = int(offset * ocr_len / gs_len) if gs_len > 0 else 0
                gs_to_ocr[i1 + offset] = j1 + min(ocr_offset, ocr_len - 1)
        elif tag == 'delete':
            for offset in range(i2 - i1):
                gs_to_ocr[i1 + offset] = j1
    
    # Build normalized to original position map for OCR
    norm_to_orig = []
    for i, c in enumerate(ocr_combined):
        c_norm = normalize_text(c)
        if c_norm:  # Not empty after normalization
            norm_to_orig.append(i)
    
    # Process each GS line
    output_lines = []
    gs_pos = 0
    ocr_pos_used = 0  # Track where we are in original OCR text
    consecutive_missing = 0
    first_line = True
    
    for line_idx, gs_line in enumerate(gs_lines):
        has_hyphen = gs_line.rstrip().endswith('=')
        gs_line_text = gs_line.rstrip('=').strip()
        gs_line_norm = normalize_text(gs_line_text)
        
        if not gs_line_norm:
            output_lines.append('')
            continue
        
        gs_start = gs_pos
        gs_end = gs_pos + len(gs_line_norm)
        
        # Map to OCR positions
        if gs_start in gs_to_ocr and (gs_end - 1) in gs_to_ocr:
            if consecutive_missing > 0:
                if add_markup:
                    output_lines.append('<MISSINGLINE/>')
                consecutive_missing = 0
            
            ocr_start_norm = gs_to_ocr[gs_start]
            ocr_end_norm = gs_to_ocr[gs_end - 1] + 1
            
            # Special: include prefix on first line
            if first_line and ocr_start_norm > 0:
                ocr_start_norm = 0
                first_line = False
            
            # Map to original positions
            if ocr_start_norm < len(norm_to_orig) and ocr_end_norm <= len(norm_to_orig):
                orig_start_target = norm_to_orig[ocr_start_norm]
                if ocr_end_norm < len(norm_to_orig):
                    orig_end_target = norm_to_orig[ocr_end_norm]
                else:
                    orig_end_target = len(ocr_combined)
                
                # Use the position from last line as start
                orig_start = max(ocr_pos_used, orig_start_target)
                orig_end = orig_end_target
                
                # CRITICAL: Adjust to word boundaries UNLESS GS has hyphenation
                if not has_hyphen:
                    # No hyphenation - must break at word boundary
                    # Adjust end to nearest space after
                    orig_end = find_nearest_space_after(ocr_combined, orig_end)
                else:
                    # GS has hyphenation - need to split a word
                    # Get the prefix from this line and suffix from next line
                    gs_words = gs_line_text.split()
                    if gs_words and line_idx + 1 < len(gs_lines):
                        gs_last_word = gs_words[-1]  # Prefix (e.g., "Be")
                        
                        # Get first word of next GS line
                        next_gs_line = gs_lines[line_idx + 1].strip()
                        next_gs_words = next_gs_line.lstrip('=').split()
                        if next_gs_words:
                            gs_next_word = next_gs_words[0]  # Suffix (e.g., "urteilung")
                            
                            # Reconstruct the full word
                            full_word_gs = gs_last_word + gs_next_word
                            full_word_norm = normalize_text(full_word_gs)
                            prefix_norm = normalize_text(gs_last_word)
                            
                            # Search for this word in OCR starting from current position
                            search_start = orig_start
                            search_end = min(len(ocr_combined), orig_start + 200)
                            
                            # Find the word in OCR
                            found_split = False
                            pos = search_start
                            while pos < search_end:
                                # Skip spaces
                                while pos < search_end and ocr_combined[pos].isspace():
                                    pos += 1
                                
                                # Extract word
                                word_start = pos
                                while pos < search_end and not ocr_combined[pos].isspace():
                                    pos += 1
                                word = ocr_combined[word_start:pos]
                                
                                if word:
                                    word_norm = normalize_text(word)
                                    # Check if this word matches the full reconstructed word
                                    ratio = SequenceMatcher(None, full_word_norm, word_norm).ratio()
                                    if ratio >= 0.7:
                                        # Found it! Split at prefix length
                                        # Map normalized position to original
                                        char_count = 0
                                        for i, c in enumerate(word):
                                            c_norm = normalize_text(c)
                                            if c_norm:
                                                char_count += 1
                                                if char_count >= len(prefix_norm):
                                                    orig_end = word_start + i + 1
                                                    found_split = True
                                                    break
                                        break
                            
                            if not found_split:
                                # Fallback: break at word boundary
                                orig_end = find_nearest_space_after(ocr_combined, orig_end)
                    else:
                        # No next line or no words - fallback
                        orig_end = find_nearest_space_after(ocr_combined, orig_end)
                
                # Extract OCR segment
                ocr_segment = ocr_combined[orig_start:orig_end]
                ocr_segment = re.sub(r'\s+', ' ', ocr_segment).strip()
                
                # Apply transformations
                ocr_segment = ocr_segment.replace('-', '=')
                if ocr_segment.endswith('¬'):
                    ocr_segment = ocr_segment[:-1] + '='
                else:
                    ocr_segment = ocr_segment.replace('¬', '=¬')
                
                if has_hyphen and not ocr_segment.endswith('='):
                    ocr_segment += '='
                
                output_lines.append(ocr_segment)
                
                # Update position for next line
                ocr_pos_used = orig_end
                # Skip any spaces
                while ocr_pos_used < len(ocr_combined) and ocr_combined[ocr_pos_used].isspace():
                    ocr_pos_used += 1
            else:
                consecutive_missing += 1
        else:
            consecutive_missing += 1
        
        gs_pos = gs_end
    
    if consecutive_missing > 0 and add_markup:
        output_lines.append('<MISSINGLINE/>')
    
    return '\n'.join(output_lines)


def process_file_pair(ocr_file, gs_file, output_file, add_markup=False, replace_md_headers=False):
    """Process a pair of OCR and gold standard files."""
    
    with open(ocr_file, 'r', encoding='utf-8') as f:
        ocr_text = f.read()
    
    with open(gs_file, 'r', encoding='utf-8') as f:
        gs_text = f.read()
    
    reformatted = reformat_ocr_to_gs(ocr_text, gs_text, add_markup=add_markup, replace_md_headers=replace_md_headers)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(reformatted)
    
    print(f"Processed: {ocr_file} + {gs_file} -> {output_file}")


def process_file_pair_debug(ocr_file, gs_file, output_file, add_markup=False, replace_md_headers=False):
    """Process files with debug output."""
    
    with open(ocr_file, 'r', encoding='utf-8') as f:
        ocr_text = f.read()
    
    with open(gs_file, 'r', encoding='utf-8') as f:
        gs_text = f.read()
    
    ocr_cleaned = clean_ocr_text(ocr_text, replace_md_headers=replace_md_headers)
    ocr_cleaned = preprocess_text(ocr_cleaned)
    
    ocr_lines = get_lines(ocr_cleaned)
    gs_lines = get_lines(gs_text)
    
    print("=== DEBUG INFO ===")
    print(f"OCR lines: {len(ocr_lines)}")
    print(f"GS lines: {len(gs_lines)}")
    
    print("\n=== FIRST 5 OCR LINES ===")
    for i, line in enumerate(ocr_lines[:5]):
        print(f"{i}: '{line[:80]}'")
    
    print("\n=== FIRST 10 GS LINES ===")
    for i, line in enumerate(gs_lines[:10]):
        print(f"{i}: '{line}'")
    
    reformatted = reformat_ocr_to_gs(ocr_text, gs_text, add_markup=add_markup, replace_md_headers=replace_md_headers)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(reformatted)
    
    print("\n=== FIRST 10 OUTPUT LINES ===")
    for i, line in enumerate(reformatted.split('\n')[:10]):
        print(f"{i}: '{line}'")
    
    print(f"\nProcessed: {ocr_file} + {gs_file} -> {output_file}")


def main():
    if len(sys.argv) < 4:
        print("Usage: python ocr_to_gs.py <ocr_file> <gs_file> <output_file> [OPTIONS]")
        print("\nReformats OCR output to match gold standard layout.")
        print("  ocr_file: OCR result file")
        print("  gs_file: Gold standard file with original formatting")
        print("  output_file: Output file with reformatted OCR")
        print("\nOptions:")
        print("  --debug: Enable debug output")
        print("  --add-markup: Add <MISSINGLINE/> tags for alignment issues")
        print("  --md: Treat # as markdown headers (replace with newlines)")
        sys.exit(1)
    
    ocr_file = sys.argv[1]
    gs_file = sys.argv[2]
    output_file = sys.argv[3]
    debug = '--debug' in sys.argv
    add_markup = '--add-markup' in sys.argv
    replace_md_headers = '--md' in sys.argv
    
    if not os.path.exists(ocr_file):
        print(f"Error: OCR file not found: {ocr_file}")
        sys.exit(1)
    
    if not os.path.exists(gs_file):
        print(f"Error: Gold standard file not found: {gs_file}")
        sys.exit(1)
    
    if debug:
        process_file_pair_debug(ocr_file, gs_file, output_file, add_markup=add_markup, replace_md_headers=replace_md_headers)
    else:
        process_file_pair(ocr_file, gs_file, output_file, add_markup=add_markup, replace_md_headers=replace_md_headers)


if __name__ == '__main__':
    main()
