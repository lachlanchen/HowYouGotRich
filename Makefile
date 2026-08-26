.PHONY: all full pocket verify multilingual multilingual-prepare multilingual-validate multilingual-status multilingual-pdfs sync-multilingual web site verify-site serve

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
	python3 scripts/validate_multilingual.py --require-complete

multilingual-status:
	python3 scripts/report_multilingual.py

multilingual: multilingual-pdfs web

multilingual-pdfs:
	python3 scripts/build_multilingual_pdfs.py

sync-multilingual:
	./scripts/sync-multilingual-pdfs.sh

web: multilingual-validate
	python3 scripts/build-web-edition.py

site: web
	./scripts/build-site.sh

verify-site: site
	python3 scripts/validate-site.py build/site

serve: site
	python3 -m http.server 8000 --directory build/site
