APP_NAME=searx_master

build:
	docker stop $(APP_NAME):latest || true
	docker rmi -f $(APP_NAME):latest || true
	docker rm -f $(APP_NAME) || true
	docker build -t $(APP_NAME) .

run:
	docker run -d --rm -p 8888:8888 --name="$(APP_NAME)" $(APP_NAME)
	sleep 10

stop:
	docker stop $(APP_NAME)
