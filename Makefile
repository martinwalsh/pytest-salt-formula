include .makefiles/ludicrous.mk

#> install local editable package and its dependencies
install:
	pipenv install -e .

#> run tests
test: | install
	pipenv run pytest $(if $(OPTS),$(OPTS),-v) $(if $(TEST),$(TEST))

clean::
	rm -rf pytest_salt_formula.egg-info/ .pytest_cache/


.PHONY: clean test install
