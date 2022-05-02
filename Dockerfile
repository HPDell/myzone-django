FROM python:3.8

COPY . /code
WORKDIR /code

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y gettext libjpeg62-turbo libjpeg62-turbo-dev zlib1g-dev

RUN pip install -r requirements.txt
EXPOSE 8000

ENTRYPOINT [ "/bin/bash", "startup.sh" ]
