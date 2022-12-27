FROM python:3.11-alpine
USER root
RUN apk update \
    && apk add git \
    && git clone https://github.com/w531t4/alarmcenter.git \
    && cd alarmcenter \
    && git checkout 1-pip-ify-content \
    && pip install -r requirements.txt \
    && mkdir /config
ENTRYPOINT ["python3", "/alarmcenter/alarmcenter.py", "/config/config.json"]