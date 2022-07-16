FROM python:3.8-buster as builder
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

ENV HOME=/home/app
RUN mkdir -p $HOME
WORKDIR $HOME
RUN apt-get update
COPY . .
EXPOSE 3176
RUN pip install -r requirements.txt
ENTRYPOINT ["python","main_api.py"]