FROM python:3.9-slim

WORKDIR /Mbot

RUN apt-get update && apt-get install -y libssl-dev procps wget perl build-essential

COPY openssl-1.1.1u.tar.gz /Mbot

RUN mkdir -p /usr/openssl \
    && tar -xvzf openssl-1.1.1u.tar.gz -C /usr/openssl --strip-components=1

RUN cd /usr/openssl && ./config && make && make install


copy req.txt .

RUN pip install --no-cache-dir -r req.txt

COPY . .



