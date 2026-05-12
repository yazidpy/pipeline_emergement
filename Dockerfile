FROM apache/airflow:2.10.2

USER root
# Installation des dépendances système si nécessaire (ex: libpq-dev pour psycopg2)
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         build-essential \
         openjdk-17-jre-headless \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

USER airflow
# Installation des dépendances Python (depuis requirements.txt)
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade -r /requirements.txt
