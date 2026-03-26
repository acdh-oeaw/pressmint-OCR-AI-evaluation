#!/bin/bash

# Batch processor for ocr2gs.py
# Usage: ./run_ocr_to_gs_formatter.sh GOLDSTANDARDFOLDER OCRFOLDER [OUTPUTFOLDER] [OPTIONS]

set -e  # Exit on error

# Check arguments
if [ $# -lt 2 ]; then
    echo "Usage: $0 GOLDSTANDARDFOLDER OCRFOLDER [OUTPUTFOLDER] [OPTIONS]"
    echo ""
    echo "  GOLDSTANDARDFOLDER: Directory containing gold standard files"
    echo "  OCRFOLDER:          Directory containing OCR files"
    echo "  OUTPUTFOLDER:       Directory for output files (optional)"
    echo "                      Default: <OCRFOLDER>_ocr2gs"
    echo ""
    echo "Options:"
    echo "  --debug:      Enable debug output"
    echo "  --add-markup: Add <MISSINGLINE/> and <ADDEDLINE> tags"
    echo "  --md:         Treat # as markdown headers (replace with newlines)"
    exit 1
fi

GOLD_DIR="$1"
OCR_DIR="$2"

# Determine output directory
# If third argument doesn't start with --, it's the output folder
if [ $# -ge 3 ] && [[ ! "$3" =~ ^-- ]]; then
    OUTPUT_DIR="$3"
    shift 3
else
    OUTPUT_DIR="${OCR_DIR}_ocr2gs"
    shift 2
fi

# Collect remaining arguments as options
OPTIONS="$@"

# Check if input directories exist
if [ ! -d "$GOLD_DIR" ]; then
    echo "Error: Gold standard folder does not exist: $GOLD_DIR"
    exit 1
fi

if [ ! -d "$OCR_DIR" ]; then
    echo "Error: OCR folder does not exist: $OCR_DIR"
    exit 1
fi

# Create output directory if it doesn't exist
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "Creating output directory: $OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR"
fi

# Find the script location (assuming it's in the same directory or in PATH)
SCRIPT_NAME="ocr2gs.py"
SCRIPT_PATH=""

# Check common locations
if [ -f "./$SCRIPT_NAME" ]; then
    SCRIPT_PATH="./$SCRIPT_NAME"
elif [ -f "./src/utils/$SCRIPT_NAME" ]; then
    SCRIPT_PATH="./src/utils/$SCRIPT_NAME"
elif command -v "$SCRIPT_NAME" &> /dev/null; then
    SCRIPT_PATH="$SCRIPT_NAME"
else
    echo "Error: Cannot find $SCRIPT_NAME"
    echo "Please ensure the script is in the current directory, ./src/utils/, or in PATH"
    exit 1
fi

echo "Using script: $SCRIPT_PATH"
echo "Gold standard folder: $GOLD_DIR"
echo "OCR folder: $OCR_DIR"
echo "Output folder: $OUTPUT_DIR"
echo "Options: $OPTIONS"
echo ""

# Counter for processed files
processed=0
skipped=0
failed=0

# Process all files in OCR folder
for ocr_file in "$OCR_DIR"/*; do
    # Skip if not a file
    [ -f "$ocr_file" ] || continue
    
    # Get basename
    filename=$(basename "$ocr_file")
    
    # Look for matching gold standard file
    gold_file="$GOLD_DIR/$filename"
    
    if [ ! -f "$gold_file" ]; then
        echo "WARNING: No matching gold standard file for: $filename (skipping)"
        skipped=$((skipped + 1))
        continue
    fi
    
    # Output file path
    output_file="$OUTPUT_DIR/$filename"
    
    echo "Processing: $filename"
    echo "  Gold: $gold_file"
    echo "  OCR:  $ocr_file"
    echo "  Out:  $output_file"
    
    # Run the formatter with options
    if python3 "$SCRIPT_PATH" "$ocr_file" "$gold_file" "$output_file" $OPTIONS; then
        processed=$((processed + 1))
    else
        echo "ERROR: Failed to process $filename"
        failed=$((failed + 1))
    fi
    
    echo ""
done

# Summary
echo "================================"
echo "Processing complete!"
echo "  Processed: $processed"
echo "  Skipped:   $skipped (no matching gold standard)"
echo "  Failed:    $failed"
echo "================================"

if [ $failed -gt 0 ]; then
    exit 1
fi
