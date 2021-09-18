from html_parser import build_login_form
from auto import User_Agent, print1, print_with_time


import requests
import sys
import getopt


def login(username, password):
    print_with_time('Start {0} login attempt ...'.format(username))
    header = {
        'Host': 'passport.ustc.edu.cn',
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': 'windows',
        'Cache-Control': 'no-cache',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': User_Agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh,en-US;q=0.9,en;q=0.8,zh-CN;q=0.7',
    }
    url = 'https://passport.ustc.edu.cn/login'
    print1('Getting {0} ...'.format(url))
    resp = requests.get(url, headers=header)
    cookies = {}
    for k, v in resp.cookies.get_dict().items():
        cookies[k] = v
    userinfo = {
        'username': username,
        'password': password
    }
    form_str = build_login_form(resp.text, userinfo, cookies['JSESSIONID'], service='')

    url = 'https://passport.ustc.edu.cn/login'
    header['Cache-Control'] = 'max-age=0'
    header['Origin'] = 'https://passport.ustc.edu.cn/'
    header['Content-Type'] = 'application/x-www-form-urlencoded'
    header['Referer'] = 'https://passport.ustc.edu.cn/login'
    print1('Posting {0} ...'.format(url))
    resp = requests.post(url, data=form_str, headers=header, cookies=cookies, allow_redirects=False)
    success_flag = False
    try:
        if resp.headers['location'] == 'https://passport.ustc.edu.cn/success.jsp':
            success_flag = True
    except BaseException as e:
        print1(str(e))
    if success_flag:
        print_with_time('{0} authentication success'.format(username))
        exit(0)
    else:
        print_with_time('{0} authentication failed'.format(username))
        exit(1)


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], '-u:-p:', ['username=', 'password='])
    except getopt.GetoptError:
        print1('input args error: login.py -u <username> -p <password>')
        sys.exit(2)
    u = ''
    p = ''
    for opt, arg in opts:
        if opt in ('-u', '--username'):
            u = arg
        if opt in ('-p', '--password'):
            p = arg
    login(u, p)
