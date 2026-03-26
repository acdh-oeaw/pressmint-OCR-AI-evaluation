SHELL := /bin/bash

clean:
	@echo -e "\nTransforming all '-' to '=' ...\n"; \
	perl -CSDA -pi -e 'use utf8; s{ä}{ä}g; s{ö}{ö}g; s{ü}{ü}g; s{Ä}{Ä}g; s{Ö}{Ö}s; s{Ü}{Ü}g;  s/\x{A0}/ /g; s{-}{=}g; s{&amp;}{&}g; s{ +$$}{}g;' *txt; \
	perl -CSDA -pi -e 'use utf8; s{J([^aeiouäöü.,:\s])}{I$$1}g;' *txt
