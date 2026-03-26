export SHELL := /bin/bash

#Usage: ./run_ocr_to_gs_batch.sh GOLDSTANDARDFOLDER OCRFOLDER [OUTPUTFOLDER] [OPTIONS]

#  GOLDSTANDARDFOLDER: Directory containing gold standard files
#  OCRFOLDER:          Directory containing OCR files
#  OUTPUTFOLDER:       Directory for output files (optional)
#                      Default: <OCRFOLDER>_ocr2gs

#Options:
#  --debug:      Enable debug output
#  --add-markup: Add <MISSINGLINE/> and <ADDEDLINE> tags
#  --md:         Treat # as markdown headers (replace with newlines)

#dots_ocr_1-4_default_pkl
#dots_ocr_1_default
#dots_ocr_3_default
#dots_ocr_4_default
#dots_ocr_6_english_extensive
#dots_ocr_6_english_extensive_pkl
#dots_ocr_7_german_extensive_2
#dots_ocr_7_german_extensive_2_pkl
#dots_ocr_default_0

TXTHOME := "$$HOME/pressmint-ground-truth/data/texts"
GS := "transkribus_corrected"


ocr2gold:
	## MIT -md
	#	for d in dots_ocr_1_default dots_ocr_4_default; do \
	#		echo -e "\n== ${TXTHOME} $$d =="; \
	#		run_ocr_to_gs_batch.sh ${TXTHOME}/${GS} ${TXTHOME}/$$d  --md  ; \
	#	done
	## OHNE -md
	for d in anno transkribus; do \
		echo -e "\n== $$d =="; \
		run_ocr_to_gs_batch.sh ${TXTHOME}/${GS} ${TXTHOME}/$$d   ; \
	done
 
