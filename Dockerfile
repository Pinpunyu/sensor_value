FROM python:latest

COPY sensor.py /app/

WORKDIR /app

RUN TZ=Asia/Taipei \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && dpkg-reconfigure -f noninteractive tzdata \
    && pip install requests && mkdir leaves

CMD python -u sensor.py
