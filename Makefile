.PHONY: start-server

start-server:
	PYTHONPATH=server/src/main/python python3 server/src/main/python/webserver/app.py
