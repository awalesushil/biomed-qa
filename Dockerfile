FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN python3 -m pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app