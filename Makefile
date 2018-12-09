.PHONY: start-server build

start-server:
	cp -rf client/ server/src/main/resources/public/
	PYTHONPATH=server/src/main/python python3 server/src/main/python/webserver/app.py

build:
	docker build -t mokemon/thesproj .

build-stack:
	echo ""