FROM python:3.10

WORKDIR /app/

RUN apt update -y && apt-get install -y cmake


ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1

RUN pip install poetry

COPY . /app/

# install dependencies
RUN poetry config virtualenvs.create false && poetry install --no-dev --no-ansi
RUN pip3 install -r requirements.txt

CMD ["bash", "run.sh"]