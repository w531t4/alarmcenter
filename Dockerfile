FROM python:3.11
USER root
RUN pip install https://github.com/w531t4/alarmcenter/archive/master.zip \
    && mkdir /config
ENTRYPOINT ["alarmcenter", "/config/config.json"]