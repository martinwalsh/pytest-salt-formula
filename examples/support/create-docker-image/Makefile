export SALT_VERSION := 2017.7.5

image:
	kitchen converge && \
		CID=$$(sed -nE 's/container_id: (.*)/\1/p' .kitchen/*.yml); \
		docker commit $$CID salt-$(SALT_VERSION)/centos-7.5
	@echo "Intermediate container saved to image named salt-$(SALT_VERSION)/centos-7.5"

clean:
	kitchen destroy
	rm -rf .kitchen

.PHONY: image clean
