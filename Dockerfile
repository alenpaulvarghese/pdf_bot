FROM python:3.10

WORKDIR /app/

RUN apt update -y && apt-get install -y cmake

COPY . /app/

RUN python -m pip install -r requirements.txt

CMD ["bash", "run.sh"]