import requests
import time
import cv2
import os


# 2021.09.14 19:05

url = 'https://passport.ustc.edu.cn/validatecode.jsp?type=login'
User_Agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'



def download_img(path, session_id):
    header = {
        'Host': 'passport.ustc.edu.cn',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': User_Agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-ch-ua': '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
        'sec-ch-ua-mobile': '?0',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh,en-US;q=0.9,en;q=0.8,zh-CN;q=0.7',
        'Cookie': 'JSESSIONID=' + session_id,
    }
    resp = requests.get(url, headers=header)
    with open(path, 'wb') as f:
        f.write(resp.content)


if __name__ == '__main__':
    for i in range(256, 512):
        path = 'images/{0}.jfif'.format(str(i))
        download_img(path, 'FC130FEFF93CB9183217640D7786AFE6')
        img = cv2.imread(path, cv2.IMREAD_COLOR)
        cv2.imwrite('images/codes/{0}.png'.format(str(i)), img)
        os.remove(path)
        time.sleep(0.1)

