FROM python:3.8

COPY . /code
WORKDIR /code

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y gettext

RUN pip install -r requirements.txt
EXPOSE 8000

ENTRYPOINT [ "/bin/bash", "startup.sh" ]
