OPTS ?= -vvx

test: unit kitchen
	@:

install:
	pipenv install --dev
	bundle install

unit:
	pipenv run pytest $(OPTS) test/unit

integration:
	bundle exec kitchen test

clean:
	bundle exec kitchen destroy
	[ -n "$$(pipenv --venv 2> /dev/null)" ] && rm -rf "$$(pipenv --venv)" || true
	rm -rf .kitchen .pytest_cache

.PHONY: test unit integration install clean
