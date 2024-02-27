import requests
import json
import logging
from datetime import datetime

# 配置日志记录器，设置日志级别和输出文件
logging.basicConfig(filename='output.log', level=logging.INFO,encoding='utf-8')
headers = {
    'Content-Type': 'application/json'  # 设置正确的 Content-Type
}
def addLivebullet(params,name):
    timestampErr=int(datetime.now().timestamp())
    dt_object = datetime.fromtimestamp(timestampErr)
    formatted_date = dt_object.strftime('%Y-%m-%d %H:%M:%S')
    logging.info(f'{name}接口调用，时间:{formatted_date}')
    data=json.dumps(params)
    print('请求接口',data)
    if len(params)==0:
        return
    
    url = 'https://xxx'  # 接口URL
    
    response = requests.post(url,headers=headers,data=data)  # 发送GET请求
    if response.status_code == 200:  # 检查响应状态码
        print(response,'接口返回数据')
        data = response.content  # 获取响应数据
        print(data,'接口返回数据')
    else:
        print('请求失败')
        response=str(response.content, 'utf-8') 
        logging.info(f'{name}:存储接口错误{response}，时间:{formatted_date}')
        print(response,'接口返回数据')