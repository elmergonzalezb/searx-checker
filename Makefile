APP_NAME=searx_checker
SEARX_URL=http://localhost:8888
OUTPUT_FILENAME=localhost.json

ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

DOCKER_INTERACTIVE_PARAM:=$(shell [ -t 0 ] && echo " -t -i")

build: ## Build the container
	docker build -t $(APP_NAME) .

run: ## Run container
	docker run $(DOCKER_INTERACTIVE_PARAM) --rm --network=host -v $(ROOT_DIR)/html/output:/opt/searx-checker/html/output --name="$(APP_NAME)" $(APP_NAME) -o html/output/$(OUTPUT_FILENAME) $(SEARX_URL)

runmaster:
	$(MAKE) -C searx build
	$(MAKE) -C searx run
	$(MAKE) run
	$(MAKE) -C searx stop

webserver:
	docker run -d --rm -p 80:80 --name searx-checker-result -v $(ROOT_DIR)/html:/usr/share/nginx/html nginx
