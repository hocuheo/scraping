.PHONY: start build stop logs build-deploy

start:
	docker-compose up -d

stop:
	docker-compose down

logs:
	docker-compose logs -f

build:
	cp -rf client/ server/src/main/resources/public/
	docker-compose build

build-deploy:
	cp -rf ./client/ ./server/src/main/resources/public/
	docker build -t mokemon/thesproj .