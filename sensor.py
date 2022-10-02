import requests
import datetime
import time

while 1:
    
    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    rt = requests.post('http://220.130.108.181:8866/serviceRTU.asmx/FunNoValueGet', json={
        "FunNo": "SF001_TEMP_No4",
    })
    rh = requests.post('http://220.130.108.181:8866/serviceRTU.asmx/FunNoValueGet', json={
        "FunNo": "SF001_HUMI_No4",
    })

    if rt.status_code == 200 and rh.status_code == 200:
        sensor = requests.post('http://114.33.145.3/api/test_sensor', json={
            "temp": rt.json()['d'],
            "humi": rh.json()['d'],
            "datetime": now_time,
        })

    time.sleep(3600)

