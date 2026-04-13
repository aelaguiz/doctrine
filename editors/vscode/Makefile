.PHONY: all deps test package

all: package

deps:
	npm ci

test: deps
	npm test

package: deps
	npm run package:vsix
