.PHONY: help build start stop delete

help: ## Display help prompt
	@echo "You can run the following commands"
	@echo ""
	@perl -nle'print $& if m{^[a-zA-Z_-]+:.*?## .*$$}' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Creates a PostgreSQL docker image
	@docker build -t crypto-db -f Dockerfile .
	mkdir -p postgres_data_blockfi

start: ## Starts the PostgreSQL docker container
	@docker run --name crypto-db -p 5432:5432 -v postgres_data_blockfi:/var/lib/postgresql/data crypto-db

stop: ## Stops the PostgreSQL docker container
	@docker stop crypto-db

delete: ## Deletes the PostgreSQL docker container, image, and data volume
	@docker rm crypto-db
	@docker rmi crypto-db
	@docker volume rm postgres_data_blockfi
	rm -rf postgres_data_blockfi

console: ## Opens a psql console
	@docker exec -it crypto-db psql -h localhost -U datascience -d blockfi
