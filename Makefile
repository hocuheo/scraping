.PHONY: start build stop logs

start:
	cp -rf client/ server/src/main/resources/public/
	docker-compose up -d

stop:
	docker-compose down

logs:
	docker-compose logs -f

build:
	docker-compose build
