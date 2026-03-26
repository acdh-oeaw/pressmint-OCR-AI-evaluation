SHELL := /bin/bash

clean:
	@echo -e "\nTransforming all '-' to '=' ...\n"; \
	perl -CSDA -pi -e 's/\x{A0}/ /g; s{-}{=}g; s{&amp;}{&}g; s{ +$$}{}g;' *txt
