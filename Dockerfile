FROM ultralytics/yolov5

COPY sensor.py /app/

WORKDIR /app

RUN apt-get update \
    && TZ=Asia/Taipei \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && dpkg-reconfigure -f noninteractive tzdata \
    && pip install requests && mkdir leaves

CMD python -u sensor.py
