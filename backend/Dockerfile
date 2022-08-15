FROM python:3.8.5

RUN apt-get update \
    && apt-get install build-essential postgresql-client libldap2-dev libsasl2-dev ldap-utils -y

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/usr/src/app

EXPOSE 8000
