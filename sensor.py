import requests
import datetime
import time
import torch
import cv2
import math
import numpy


def detect(img, video, now_time):

  model = torch.hub.load('ultralytics/yolov5', 'custom', path='leaves/yolov5m6_best.pt')
  model.iou = 0.5
  model.conf = 0.5

  results = model(img, size=1280)
  results.save(save_dir=f'leaves/detect{video}/exp')
  arr = results.pandas().xyxy[0].to_numpy()

  add_photo = cv2.imread(f'leaves/video{video}_add.png')
  hybrid = numpy.zeros(add_photo.shape)
  total_leaves = 0
  for i in range(0, add_photo.shape[0]):
    for j in range(0, add_photo.shape[1]):
      if (add_photo[i, j] == numpy.array([0, 0, 0])).all():
        total_leaves += 1
      else:
        hybrid[i][j] = numpy.array([255, 255, 255])

  for i in arr:

    flag = 0
    for x in range(1, 4, 2):
      for y in range(0, 3, 2):
        if (add_photo[math.floor(i[x]), math.floor(i[y])] == numpy.array([255, 255, 255])).all():
          flag = 1
    if flag:
      continue

    for ii in range(math.floor(i[0]), math.floor(i[2])):
      for jj in range(math.floor(i[1]), math.floor(i[3])):
        hybrid[jj][ii] = numpy.array([255, 0, 0])

  blue = 0
  for i in range(0, hybrid.shape[0]):
    for j in range(0, hybrid.shape[1]):
      if (hybrid[i, j] == numpy.array([255, 0, 0])).all():
        blue += 1

  print(f'{(1-blue/total_leaves)*100}%')
  cv2.imwrite(
      f'leaves/color{video}/color{video}_{now_time}.png', hybrid)
  return (1-blue/total_leaves)*100

def login(account, password):
  account = requests.post(
      f'http://114.33.145.3/api/users/login',
      json={
          "account": account,
          "password": password
      }, timeout=5)
  return account

def get_sensor_data(type):
  data = requests.post('http://220.130.108.181:8866/serviceRTU.asmx/FunNoValueGet', json={
      "FunNo": f"SF001_{type}_No4",
  }, timeout=5)
  return data

def create_sensor_data(url, headers, data, smallBlockId, id):
  req = requests.post(
      f'http://114.33.145.3/api/{url}',
      headers=headers,
      json={
          "value": data,
          "smallBlockId": smallBlockId,
          "sensorId": id
      }, timeout=5)
  return req

def refresh_token(id, refreshToken):
  refresh = requests.post('http://114.33.145.3/api/users/token',
                          json={
                              "userId": id,
                              "token": refreshToken
                          }, timeout=5)
  return refresh



url = ["healthDatas/addHealthData", "humidityDatas/addHumidityData",
       "temperatureDatas/addtemperatureData"]
smallBlockId = [1,2,6]

account = login("sensor", "123sensor")
accessToken = account.json()['accessToken']
refreshToken = account.json()['refreshToken']
id = account.json()['user']['id']
headers = {'Authorization': f'Bearer {accessToken}'}

while 1:

    now_time = datetime.datetime.now().strftime('%Y-%m-%d,%H-%M-%S')
    minute_date = datetime.datetime.now().strftime('%Y-%m-%d,%H-%M-%S')[-5:-3]

    if minute_date == '50' :

      check = requests.post('http://114.33.145.3/api/sensors/allSensors',
                            headers=headers, timeout=5)
      if check.status_code == 403:
          refresh = refresh_token(id, refreshToken)
          accessToken = refresh.json()['accessToken']
          refreshToken = refresh.json()['refreshToken']
          headers = {'Authorization': f'Bearer {accessToken}'}

      rh = get_sensor_data("HUMI").json()['d']
      rt = get_sensor_data("TEMP").json()['d']

      for i in range(2, 5):
        
        try:
          err = f'video{i-1}'

          img_data = requests.get(
              f'http://219.86.140.31:890{i}/cgi-bin/viewer/video.jpg?streamid=0', auth=('root', 'a7075701'), timeout=5)
          pic_path = f'leaves/video{i-1}/video{i-1}_{now_time}.png'
          with open(pic_path, 'wb') as handler:
              handler.write(img_data.content)

          value = [round(detect(pic_path, i-1, now_time), 1), rh, rt]

          for sensor in range(0, 3):
            data = create_sensor_data(
                url[sensor], headers, value[sensor], smallBlockId[i-2], 3-sensor)

        except:
          print(f"{err} Error")

    time.sleep(60)

