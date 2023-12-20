FROM       python:alpine

RUN        mkdir /app
WORKDIR    /app
ADD        requirements.txt /app/
RUN        pip install -r requirements.txt
ADD        . /app

ENTRYPOINT ["python", "check.py"]
