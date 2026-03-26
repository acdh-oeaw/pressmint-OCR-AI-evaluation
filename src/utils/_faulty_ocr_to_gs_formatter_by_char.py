#!/usr/bin/env python3
"""
OCR to Gold Standard Formatter
Reformats OCR output to match gold standard layout for easier comparison.
"""

import sys
import os
from difflib import SequenceMatcher
import re


def clean_ocr_text(text):
    """Clean OCR text: replace # with newlines."""
    # Replace all # characters with newlines
    text = text.replace('#', '\n')
    # NOTE: Do NOT replace - with = here, as it would break alignment
    # We'll do that after extraction
    return text


def normalize_for_matching(text):
    """Normalize text for matching: remove all whitespace and hyphenation."""
    # Remove = followed by optional whitespace and newline (word continuation)
    text = re.sub(r'=\s*\n\s*', '', text)
    # Remove all whitespace
    text = re.sub(r'\s+', '', text)
    return text


def get_gs_lines_info(gs_text):
    """Extract line information from gold standard."""
    lines_info = []
    
    for line in gs_text.split('\n'):
        stripped = line.strip()
        
        if not stripped:
            lines_info.append({
                'original': '',
                'normalized': '',
                'has_hyphen': False,
                'is_empty': True,
                'length': 0
            })
            continue
        
        has_hyphen = stripped.endswith('=')
        
        if has_hyphen:
            # Remove = for normalization
            text_without_hyphen = stripped[:-1]
        else:
            text_without_hyphen = stripped
        
        normalized = normalize_for_matching(text_without_hyphen)
        
        lines_info.append({
            'original': stripped,
            'normalized': normalized,
            'has_hyphen': has_hyphen,
            'is_empty': False,
            'length': len(normalized)
        })
    
    return lines_info


def extract_from_original_by_normalized_positions(original_text, start_norm_pos, end_norm_pos):
    """
    Extract text from original by counting non-whitespace characters.
    start_norm_pos and end_norm_pos are positions in the normalized (no-whitespace) version.
    """
    result = []
    norm_char_count = 0
    started = False
    
    for char in original_text:
        is_whitespace = char in ' \t\n\r'
        
        if not is_whitespace:
            # This is a non-whitespace character
            if norm_char_count == start_norm_pos:
                started = True
            
            if started:
                if norm_char_count >= end_norm_pos:
                    break
                result.append(char)
            
            norm_char_count += 1
        else:
            # Whitespace - include if we've started and haven't finished
            if started and norm_char_count < end_norm_pos:
                # Convert newlines to spaces
                if char == '\n':
                    result.append(' ')
                elif char == ' ':
                    result.append(char)
    
    # Clean up result
    text = ''.join(result)
    # Normalize multiple spaces
    text = re.sub(r' +', ' ', text)
    return text.strip()


def reformat_ocr_to_gs(ocr_text, gs_text):
    """Reformat OCR text to match gold standard layout."""
    
    # Step 1: Clean OCR (replace # with newlines)
    ocr_cleaned = clean_ocr_text(ocr_text)
    
    # Step 2: Normalize both texts
    ocr_normalized = normalize_for_matching(ocr_cleaned)
    gs_normalized = normalize_for_matching(gs_text)
    
    # Step 3: Get gold standard line structure
    gs_lines_info = get_gs_lines_info(gs_text)
    
    # Step 4: Create character-level alignment
    matcher = SequenceMatcher(None, gs_normalized, ocr_normalized)
    
    # Build precise mapping from GS normalized position to OCR normalized position
    # Also track which GS positions are in 'delete' blocks (GS has char, OCR doesn't)
    gs_to_ocr_map = {}
    gs_is_deleted = set()  # GS positions that don't exist in OCR
    
    for tag, gs_i1, gs_i2, ocr_j1, ocr_j2 in matcher.get_opcodes():
        if tag == 'equal':
            # Perfect match - 1-to-1 mapping
            for offset in range(gs_i2 - gs_i1):
                gs_to_ocr_map[gs_i1 + offset] = ocr_j1 + offset
        elif tag == 'replace':
            # Mismatched content - proportional mapping
            gs_len = gs_i2 - gs_i1
            ocr_len = ocr_j2 - ocr_j1
            for gs_offset in range(gs_len):
                # Map proportionally
                if gs_len > 0:
                    ocr_offset = int(gs_offset * ocr_len / gs_len)
                    ocr_offset = min(ocr_offset, ocr_len - 1)  # Clamp
                else:
                    ocr_offset = 0
                gs_to_ocr_map[gs_i1 + gs_offset] = ocr_j1 + ocr_offset
        elif tag == 'delete':
            # GS has content not in OCR - these are "deleted" characters
            for gs_offset in range(gs_i2 - gs_i1):
                gs_pos = gs_i1 + gs_offset
                gs_to_ocr_map[gs_pos] = ocr_j1  # Map to insertion point
                gs_is_deleted.add(gs_pos)  # Mark as deleted
        elif tag == 'insert':
            # OCR has content not in GS - no direct mapping needed
            pass
    
    # Step 5: Build output line by line
    output_lines = []
    gs_norm_pos = 0
    
    for line_info in gs_lines_info:
        if line_info['is_empty']:
            output_lines.append('')
            continue
        
        line_length = line_info['length']
        
        # Map GS range to OCR range
        gs_start = gs_norm_pos
        gs_end = gs_norm_pos + line_length
        
        # Get corresponding OCR positions
        if gs_start in gs_to_ocr_map:
            ocr_start = gs_to_ocr_map[gs_start]
            
            # Find the last non-deleted GS character in this line
            last_real_gs_pos = gs_end - 1
            while last_real_gs_pos >= gs_start and last_real_gs_pos in gs_is_deleted:
                last_real_gs_pos -= 1
            
            if last_real_gs_pos >= gs_start and last_real_gs_pos in gs_to_ocr_map:
                # Use the position after the last real character
                ocr_end = gs_to_ocr_map[last_real_gs_pos] + 1
            else:
                # All characters in this line are deleted, use start position
                ocr_end = ocr_start
            
            # Extract from OCR using normalized positions
            ocr_segment = extract_from_original_by_normalized_positions(
                ocr_cleaned, ocr_start, ocr_end
            )
            
            # Replace all - with = in the extracted segment
            ocr_segment = ocr_segment.replace('-', '=')
            
            # Handle ¬ character:
            # If at end of segment: replace with =
            # If not at end: replace with =¬
            if ocr_segment.endswith('¬'):
                ocr_segment = ocr_segment[:-1] + '='
            else:
                ocr_segment = ocr_segment.replace('¬', '=¬')
            
            # Add hyphen if GS line has it
            if line_info['has_hyphen']:
                output_lines.append(ocr_segment + '=')
            else:
                output_lines.append(ocr_segment)
        else:
            # Mapping failed - output empty line
            output_lines.append('')
        
        gs_norm_pos = gs_end
    
    return '\n'.join(output_lines)


def process_file_pair(ocr_file, gs_file, output_file):
    """Process a pair of OCR and gold standard files."""
    
    # Read files
    with open(ocr_file, 'r', encoding='utf-8') as f:
        ocr_text = f.read()
    
    with open(gs_file, 'r', encoding='utf-8') as f:
        gs_text = f.read()
    
    # Reformat
    reformatted = reformat_ocr_to_gs(ocr_text, gs_text)
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(reformatted)
    
    print(f"Processed: {ocr_file} + {gs_file} -> {output_file}")


def process_file_pair_debug(ocr_file, gs_file, output_file):
    """Process files with debug output."""
    
    # Read files
    with open(ocr_file, 'r', encoding='utf-8') as f:
        ocr_text = f.read()
    
    with open(gs_file, 'r', encoding='utf-8') as f:
        gs_text = f.read()
    
    # Clean and normalize
    ocr_cleaned = clean_ocr_text(ocr_text)
    ocr_normalized = normalize_for_matching(ocr_cleaned)
    gs_normalized = normalize_for_matching(gs_text)
    
    print("=== DEBUG INFO ===")
    print(f"OCR normalized length: {len(ocr_normalized)}")
    print(f"GS normalized length: {len(gs_normalized)}")
    print(f"\nFirst 200 chars of OCR normalized:\n{ocr_normalized[:200]}")
    print(f"\nFirst 200 chars of GS normalized:\n{gs_normalized[:200]}")
    
    # Show the alignment around position 110
    print(f"\n=== ALIGNMENT AROUND POSITION 110 ===")
    print(f"GS [105-115]: '{gs_normalized[105:115]}'")
    print(f"OCR[105-115]: '{ocr_normalized[105:115]}'")
    
    # Create alignment
    matcher = SequenceMatcher(None, gs_normalized, ocr_normalized)
    print(f"\n=== OPCODES ===")
    for tag, gs_i1, gs_i2, ocr_j1, ocr_j2 in matcher.get_opcodes():
        if gs_i1 <= 115 and gs_i2 >= 105:  # Only show relevant range
            print(f"{tag:8} GS[{gs_i1:3}-{gs_i2:3}]='{gs_normalized[gs_i1:gs_i2][:30]}' -> OCR[{ocr_j1:3}-{ocr_j2:3}]='{ocr_normalized[ocr_j1:ocr_j2][:30]}'")
    
    # Get lines
    gs_lines_info = get_gs_lines_info(gs_text)
    
    print(f"\n=== FIRST 10 GS LINES ===")
    for i, line_info in enumerate(gs_lines_info[:10]):
        print(f"Line {i}: '{line_info['original']}' (normalized: '{line_info['normalized'][:50]}...' len={line_info['length']})")
    
    # Reformat
    reformatted = reformat_ocr_to_gs(ocr_text, gs_text)
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(reformatted)
    
    print(f"\n=== OUTPUT (first 10 lines) ===")
    for i, line in enumerate(reformatted.split('\n')[:10]):
        print(f"Line {i}: '{line}'")
    
    print(f"\nProcessed: {ocr_file} + {gs_file} -> {output_file}")


def main():
    if len(sys.argv) < 4:
        print("Usage: python ocr_to_gs.py <ocr_file> <gs_file> <output_file> [--debug]")
        print("\nReformats OCR output to match gold standard layout.")
        print("  ocr_file: OCR result file")
        print("  gs_file: Gold standard file with original formatting")
        print("  output_file: Output file with reformatted OCR")
        print("  --debug: Enable debug output")
        sys.exit(1)
    
    ocr_file = sys.argv[1]
    gs_file = sys.argv[2]
    output_file = sys.argv[3]
    debug = '--debug' in sys.argv
    
    # Check files exist
    if not os.path.exists(ocr_file):
        print(f"Error: OCR file not found: {ocr_file}")
        sys.exit(1)
    
    if not os.path.exists(gs_file):
        print(f"Error: Gold standard file not found: {gs_file}")
        sys.exit(1)
    
    # Process
    if debug:
        process_file_pair_debug(ocr_file, gs_file, output_file)
    else:
        process_file_pair(ocr_file, gs_file, output_file)


if __name__ == '__main__':
    main()
