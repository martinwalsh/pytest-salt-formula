OPTS ?= -vvx

test: test-unit test-kitchen
	@:

install:
	pipenv install --dev

test-unit:
	pipenv run pytest $(OPTS) test/unit

test-kitchen:
	bundle exec kitchen test

.PHONY: test test-unit test-kitchen
