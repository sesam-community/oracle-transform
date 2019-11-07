FROM python:3.6
MAINTAINER Gabriell Vig <gabriell.vig@sesam.io>


RUN apt-get update \
    && apt-get -y install unzip \
    && apt-get -y install libaio-dev \
    && mkdir -p /opt/data/api

ADD ./oracle-instantclient/ /opt/data
ADD ./install-instantclient.sh /opt/data
ADD ./requirements.txt /opt/data
ADD api/oracle_connection.py /opt/data/api
ADD ./api/service.py /opt/data/api
ADD ./api/handlers.py /opt/data/api
RUN ["chmod", "+x", "/opt/data/install-instantclient.sh"]

WORKDIR /opt/data

ENV ORACLE_HOME=/opt/oracle/instantclient
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ORACLE_HOME

ENV OCI_HOME=/opt/oracle/instantclient
ENV OCI_LIB_DIR=/opt/oracle/instantclient
ENV OCI_INCLUDE_DIR=/opt/oracle/instantclient/sdk/include


RUN ./install-instantclient.sh \
    && pip install -r requirements.txt

EXPOSE 5000/tcp

CMD ["python","./api/service.py"]
