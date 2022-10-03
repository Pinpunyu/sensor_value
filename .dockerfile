FROM python

WORKDIR /Users/lipinyu/Desktop/python/server_docker

COPY server.py ./


CMD [ "python", "server.py" ]
