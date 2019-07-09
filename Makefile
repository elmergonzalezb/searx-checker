APP_NAME=searx/searx-checker:latest
CONTAINER_NAME=searx-checker
SEARX_URL=http://localhost:8888
OUTPUT_FILENAME=status.json

ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

DOCKER_INTERACTIVE_PARAM:=$(shell [ -t 0 ] && echo " -t -i")

build: ## Build the container
	docker build -t $(APP_NAME) .

run: ## Run container : once
	docker run $(DOCKER_INTERACTIVE_PARAM) --rm --network=host -v $(ROOT_DIR)/html/data:/usr/local/searx-checker/html/data --name="$(CONTAINER_NAME)" $(APP_NAME) -o html/data/$(OUTPUT_FILENAME) $(SEARX_URL)

cron: ## Run container : cron
	docker run $(DOCKER_INTERACTIVE_PARAM) --rm --network=host -v $(ROOT_DIR)/html/data:/usr/local/searx-checker/html/data --name="$(CONTAINER_NAME)" $(APP_NAME) -cron -o html/data/$(OUTPUT_FILENAME) $(SEARX_URL)

runmaster:
	$(MAKE) -C searx build
	$(MAKE) -C searx run
	$(MAKE) run
	$(MAKE) -C searx stop

webserver:
	docker run -d --rm -p 80:80 --name searx-checker-result -v $(ROOT_DIR)/html:/usr/share/nginx/html nginx
