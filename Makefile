.PHONY: all full pocket verify web site verify-site serve

all: full pocket

full:
	./scripts/build.sh

pocket:
	./scripts/build-pocket.sh

verify:
	./scripts/verify.sh

web:
	python3 scripts/build-web-edition.py

site: web
	./scripts/build-site.sh

verify-site: site
	python3 scripts/validate-site.py build/site

serve: site
	python3 -m http.server 8000 --directory build/site
