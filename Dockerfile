FROM ubuntu:xenial

RUN apt-get dist-upgrade -y \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
          language-pack-en \
          curl \
          python3 python3-dev python3-pip python3-setuptools \
          unzip \
          wget

RUN apt-get install -y --no-install-recommends gcc build-essential libxml2-dev libxslt1-dev zlib1g-dev openssl libssl-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/
WORKDIR /app/

COPY server/ /app/
COPY server/requirements.txt /app/

RUN pip3 install --upgrade setuptools wheel

RUN pip3 install -r /app/requirements.txt

ENV LANG=en_US.UTF-8
ENV PYTHONPATH=/app/src/main/python

CMD ["python3", "/app/src/main/python/webserver/app.py"]
