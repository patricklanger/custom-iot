FROM alpine:latest

RUN apk update && apk add \
    curl \
    git \
    vim \
    make

COPY . .

WORKDIR .

