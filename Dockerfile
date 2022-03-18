FROM python:3.8

COPY . /code
WORKDIR /code

RUN pip install -r requirements.txt
EXPOSE 8000

ENTRYPOINT [ "/bin/bash", "startup.sh" ]
