.PHONY: all full pocket verify multilingual-prepare multilingual-validate web site verify-site serve

all: full pocket

full:
	./scripts/build.sh

pocket:
	./scripts/build-pocket.sh

verify:
	./scripts/verify.sh

multilingual-prepare:
	python3 scripts/prepare_multilingual.py

multilingual-validate:
	python3 scripts/prepare_multilingual.py --check
	python3 scripts/validate_multilingual.py

web:
	python3 scripts/build-web-edition.py

site: web
	./scripts/build-site.sh

verify-site: site
	python3 scripts/validate-site.py build/site

serve: site
	python3 -m http.server 8000 --directory build/site
