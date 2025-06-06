FROM python:3.10-slim

RUN apt-get update -y && \
	apt install -y wget make

RUN pip install --upgrade pip

WORKDIR /app

COPY ./ ./

RUN pip install --requirement requirements.txt

EXPOSE 8088