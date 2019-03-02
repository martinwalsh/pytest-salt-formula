OPTS ?= -vvx

test-all: unit-all integration-all
	@:

install:
	pipenv install --dev
	bundle install

unit-all:
	@for formula in `ls -d formulas/*`; do \
		( cd $$formula && make --no-print-directory test ); \
	done

integration-all:
	@for formula in `ls -d formulas/*`; do \
		( cd $$formula && make --no-print-directory test ); \
	done

clean:
	@for formula in `ls -d formulas/*`; do \
		( cd $$formula && make --no-print-directory clean ); \
	done

.PHONY: test-all unit-all integration-all clean
