.PHONY: all full pocket verify

all: full pocket

full:
	./scripts/build.sh

pocket:
	./scripts/build-pocket.sh

verify:
	./scripts/verify.sh
