import requests
import datetime
import time

while 1:

    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for i in range(2, 5):

        try:
            img_data = requests.get(
                f'http://219.86.140.31:890{i}/cgi-bin/viewer/video.jpg?streamid=0', auth=('root', 'a7075701'), timeout=1)
            with open(f'server_docker/video{i-1}_{now_time}.jpg', 'wb') as handler:
                handler.write(img_data.content)
        except:
            pass

    try:
        rt = requests.post('http://220.130.108.181:8866/serviceRTU.asmx/FunNoValueGet', json={
            "FunNo": "SF001_TEMP_No4",
        })
        rh = requests.post('http://220.130.108.181:8866/serviceRTU.asmx/FunNoValueGet', json={
            "FunNo": "SF001_HUMI_No4",
        })

        sensor = requests.post('http://114.33.145.3/api/test_sensor', json={
            "temp": rt.json()['d'],
            "humi": rh.json()['d'],
            "datetime": now_time,
        })

    except:
        pass

    time.sleep(3600)
