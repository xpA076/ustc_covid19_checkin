import requests
import re
import time
import sys
import getopt
from html_parser import *

User_Agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'


def load_users(_path):
    _users = []
    with open(_path, 'r', encoding='UTF-8') as r:
        lines = r.readlines()
        for line in lines:
            line = line.replace(' ', '')
            if (len(line) == 0) or (re.match(r'^[A-Z]{2}\d{8},[^,]*,(\d|\d-\d),\d{6}', line) is None):
                continue
            spl = line.split(',')
            _users.append({
                'username': spl[0],
                'password': spl[1],
                'now_status': spl[2],
                'postcode': spl[3],
            })
        return _users


def update_cookies(cookies_dict, new_cookies_dict):
    for k, v in new_cookies_dict:
        cookies_dict[k] = v
    return cookies_dict


def print_with_time(print_text):
    whole_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ' -> ' + print_text
    print(whole_str)
    month_str = time.strftime("%Y-%m", time.localtime())
    with open('checkin-' + month_str + '.log', 'a+') as log_f:
        log_f.write(whole_str + '\n')


# now_status 对应当前状态:
#   1-正常在校园内, 2-正常在家, 3-居家留观, 4-集中留观, 5-住院治疗, 6-其它
# 若地址编号为 340100(合肥), 需添加在校信息：
#   2-东区, 3-南区, 4-中区, 5-北区, 6-西区, 7-先研院, 8-国金院, 9-其他院区, 0-校外
def build_report_form(token, postcode, now_status):
    now_province = postcode[0:2] + '0000'
    now_city = postcode[0:4] + '00'
    now_country = postcode
    form_dict = {
        '_token': token,
        'now_address': '1',# 内地
        'gps_now_address': '',
        'now_province': now_province,
        'gps_province': '',
        'now_city': now_city,
        'gps_city': '',
        'now_country': now_country,
        'gps_country': '',
        'now_detail': '',
        'body_condition': '1',
        'body_condition_detail': '',
        'now_status': now_status.split('-')[0],
        'now_status_detail': '',
        'has_fever': '0',
        'last_touch_sars': '0',
        'last_touch_sars_date': '',
        'last_touch_sars_detail': '',
        'is_danger': '0',
        'is_goto_danger': '0',
        'other_detail': ''
    }
    form_str = ''
    for k in form_dict.keys():
        form_str = form_str + k + '=' + form_dict[k] + '&'
        if k == 'now_detail' and now_city == '340100':
            form_str = form_str + 'is_inschool=' + now_status.split('-')[1] + '&'
    form_str = form_str[0:-1]
    return form_str


def auto_checkin(userinfo):
    print_with_time('Start')
    header = {
        'Host': 'weixine.ustc.edu.cn',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': User_Agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh,en-US;q=0.9,en;q=0.8,zh-CN;q=0.7'
    }

    cookies_checkin = {}
    url = 'https://weixine.ustc.edu.cn/2020/'
    print('Getting ' + url + ' ...')
    resp = requests.get(url, headers=header)
    cookies_checkin = update_cookies(cookies_checkin, resp.cookies.get_dict().items())

    url = 'https://weixine.ustc.edu.cn/2020/login'
    print('Getting ' + url + ' ...')
    resp = requests.get(url, headers=header)
    cookies_checkin = update_cookies(cookies_checkin, resp.cookies.get_dict().items())

    # 修改header
    url = 'https://weixine.ustc.edu.cn/2020/caslogin'
    header['Sec-Fetch-Site'] = 'same-origin'
    header['Referer'] = url
    print('Getting ' + url + ' ...')
    # 返回302, 禁止自动跳转
    resp = requests.get(url, headers=header, cookies=cookies_checkin, allow_redirects=False)
    cookies_checkin = update_cookies(cookies_checkin, resp.cookies.get_dict().items())

    url = 'https://passport.ustc.edu.cn/login?service=https%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin'
    header['Host'] = 'passport.ustc.edu.cn'
    # header['Sec-Fetch-Site'] = 'same-site'
    print('Getting ' + url + ' ...')
    resp = requests.get(url, headers=header, allow_redirects=False)
    cookie_dict_passport = {}
    cookie_dict_passport = update_cookies(cookie_dict_passport, resp.cookies.get_dict().items())

    url = 'https://passport.ustc.edu.cn/login'
    header['Referer'] = 'https://passport.ustc.edu.cn/login?service=https%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin'
    header_post = header.copy()
    header_post['Cache-Control'] = 'max-age=0'
    header_post['Content-Type'] = 'application/x-www-form-urlencoded'
    header_post['Origin'] = 'https://passport.ustc.edu.cn'
    print('Posting ' + url + ' ...')
    resp = requests.post(url,
                         data='model=uplogin.jsp&service=https%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin&warn'
                              '=&showCode=&username=' + userinfo['username'] + '&password=' + userinfo['password'] + '&button=',
                         headers=header_post,
                         cookies=cookie_dict_passport,
                         allow_redirects=False)
    # response 302, header的location项中含名为ticket的token, 和 weixine 下的 cookie 一起提交完成身份验证
    try:
        url = resp.headers['location']
        if re.search(r'ticket=ST', url) is None:
            raise BaseException('cannot get CAS-ticket')
        '''
        if resp.status_code != 302:

            '''
    except BaseException as e:
        print_with_time('Authentication failure')
        print(e)
        exit(0)
    print_with_time('Authentication success')

    header['Host'] = 'weixine.ustc.edu.cn'
    header['Sec-Fetch-Site'] = 'same-site'
    header['Cache-Control'] = 'max-age=0'
    header['Referer'] = 'https://passport.ustc.edu.cn/login'
    print('Getting ' + url + ' ...')
    resp = requests.get(url, headers=header, cookies=cookies_checkin, allow_redirects=False)
    cookies_checkin = update_cookies(cookies_checkin, resp.cookies.get_dict().items())

    url = 'https://weixine.ustc.edu.cn/2020/caslogin'
    print('Getting ' + url + ' ...')
    resp = requests.get(url, headers=header, cookies=cookies_checkin, allow_redirects=False)
    cookies_checkin = update_cookies(cookies_checkin, resp.cookies.get_dict().items())

    url = 'https://weixine.ustc.edu.cn/2020/'
    header.pop('Referer')
    print('Getting ' + url + ' ...')
    resp = requests.get(url, headers=header, cookies=cookies_checkin, allow_redirects=False)
    cookies_checkin = update_cookies(cookies_checkin, resp.cookies.get_dict().items())

    url = 'https://weixine.ustc.edu.cn/2020/home'
    header['Sec-Fetch-Site'] = 'cross-site'
    print('Getting ' + url + ' ...')
    resp = requests.get(url, headers=header, cookies=cookies_checkin, allow_redirects=False)
    cookies_checkin = update_cookies(cookies_checkin, resp.cookies.get_dict().items())

    # 验证是否获取到身份验证页面
    if resp.status_code != 200:
        print_with_time(userinfo['username'] + ' cannot get to login page')
        return 'failed'

    # 获取页面 form 中 x_csrf_token 等相关信息
    info = get_info(resp.text)
    print_with_time(info['uid'] + ' last check in : ' + info['time'] + ', token : ' + info['token'])

    # 模拟网页的两个ajax请求
    header_ajax = {
        'Host': 'weixine.ustc.edu.cn',
        'Connection': 'keep-alive',
        'Content-Length': '0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'DNT': '1',
        'X-CSRF-TOKEN': info['token'],
        'User-Agent': User_Agent,
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://weixine.ustc.edu.cn',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://weixine.ustc.edu.cn/2020/home',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh,en-US;q=0.9,en;q=0.8,zh-CN;q=0.7'
    }

    url = 'https://weixine.ustc.edu.cn/2020/get_province'
    print('Ajax ' + url + ' ...')
    resp = requests.post(url, headers=header_ajax, cookies=cookies_checkin)
    cookies_checkin = update_cookies(cookies_checkin, resp.cookies.get_dict().items())

    url = 'https://weixine.ustc.edu.cn/2020/get_city/' + userinfo['postcode'][0:2] + '0000'
    print('Ajax ' + url + ' ...')
    resp = requests.post(url, headers=header_ajax, cookies=cookies_checkin)
    cookies_checkin = update_cookies(cookies_checkin, resp.cookies.get_dict().items())

    # 提交 daily_report
    # 是的没有拼错 daliy_report, :-)
    url = 'https://weixine.ustc.edu.cn/2020/daliy_report'
    header_report = header.copy()
    header_report['Sec-Fetch-Site'] = 'same-origin'
    header_report['Referer'] = 'https://weixine.ustc.edu.cn/2020/home'
    header_report['Origin'] = 'https://weixine.ustc.edu.cn'
    header_report['Content-Type'] = 'application/x-www-form-urlencoded'
    # 填写表单 data
    report_data = build_report_form(info['token'], userinfo['postcode'], userinfo['now_status'])
    print('Posting ' + url + ' ...')
    resp = requests.post(url, data=report_data, headers=header_report, cookies=cookies_checkin,
                         allow_redirects=False)
    cookies_checkin = update_cookies(cookies_checkin, resp.cookies.get_dict().items())

    url = 'https://weixine.ustc.edu.cn/2020/home'
    header['Referer'] = 'https://weixine.ustc.edu.cn/2020/home'
    print('Getting ' + url + ' ...')
    resp = requests.get(url, headers=header, cookies=cookies_checkin, allow_redirects=False)
    cookies_checkin = update_cookies(cookies_checkin, resp.cookies.get_dict().items())
    info = get_info(resp.text)

    print_with_time(info['uid'] + ' last check in : ' + info['time'])
    print_with_time('Finish')




if __name__ == '__main__':
    path = 'keys.txt'
    users = load_users(path)
    print_with_time(str(len(users)) + ' user(s) found in ' + path)

    if len(sys.argv) > 1:
        try:
            opts, args = getopt.getopt(sys.argv[1:], '-i:', 'idx=')
        except getopt.GetoptError:
            print('input args error: auto.py -i <user index>')
            sys.exit(2)
        for opt, arg in opts:
            if opt in ('-i', '--idx'):
                i = int(arg)
                auto_checkin(users[i])
    else:
        for i in range(len(users)):
            auto_checkin(users[i])
            if i < len(users) - 1:
                time.sleep(60)
