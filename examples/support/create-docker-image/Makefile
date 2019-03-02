export SALT_VERSION := 2018.3.3

default:
	@:

image:
	bundle exec kitchen converge && \
		CID=$$(sed -nE 's/container_id: (.*)/\1/p' .kitchen/*.yml); \
		docker commit $$CID salt-$(SALT_VERSION)/centos7
	@echo "Intermediate container saved to image named salt-$(SALT_VERSION)/centos7"

clean:
	bundle exec kitchen destroy
	rm -rf .kitchen

.PHONY: default image clean
