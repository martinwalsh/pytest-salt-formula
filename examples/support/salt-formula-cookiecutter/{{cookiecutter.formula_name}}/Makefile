OPTS ?= -vvx

test: test-unit test-kitchen
	@:

install:
	pipenv install --dev
	bundle install

test-unit:
	pipenv run pytest $(OPTS) test/unit

test-kitchen:
	bundle exec kitchen test

clean:
	kitchen destroy
	[ -n "$$(pipenv --venv 2> /dev/null)" ] && rm -rf "$$(pipenv --venv)" || true
	rm -rf .kitchen .pytest_cache

.PHONY: test test-unit test-kitchen install clean
