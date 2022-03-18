import requests
import re
import time
import datetime
import sys
import getopt
import base64
import random
from html_parser import *

User_Agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'


def db_find_apply_date(username):
    with open('db.dat', 'rb') as rdb:
        rbs = rdb.read()
        for ib in range(0, len(rbs), 18):
            if str(rbs[ib:ib + 10], 'utf-8') == username:
                return str(rbs[ib + 10:ib + 18], 'utf-8')
    return ''


def db_set_apply_date(username, date_str):
    with open('db.dat', 'rb') as rdb:
        rbs = rdb.read()
    with open('db.dat', 'wb') as wdb:
        for ib in range(0, len(rbs), 18):
            if str(rbs[ib:ib + 10], 'utf-8') == username:
                wdb.write(bytes(date_str, 'utf-8'))
                return
        wdb.write(bytes(username + date_str, 'utf-8'))


def print1(line):
    print(line, flush=True)


def parse_info_str(line):
    spl = line.split(',')
    base_info = {
        'username': spl[0],
        'password': spl[1],
        'now_status': spl[2],
        'postcode': spl[3],
        'emg_name': spl[4],
        'emg_relation': spl[5],
        'emg_mobile': spl[6],
        'last_apply': ''
    }

    if len(spl) == 7:
        return base_info
    else:
        base_info['last_apply'] = spl[7]
        return base_info


def load_users(_path):
    _users = []
    with open(_path, 'r', encoding='UTF-8') as r:
        lines = r.readlines()
        for line in lines:
            line = line.replace(' ', '')
            if (len(line) == 0) or (re.match(r'^[A-Z]{2}\d{8},[^,]*,(\d|\d-\d),\d{6}', line) is None):
                continue
            _users.append(parse_info_str(line))
        return _users


def update_cookies(cookies_dict, new_cookies_dict):
    for k, v in new_cookies_dict:
        cookies_dict[k] = v
    return cookies_dict


def print_with_time(print_text):
    whole_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ' -> ' + print_text
    print(whole_str, flush=True)
    month_str = time.strftime("%Y-%m", time.localtime())
    with open('checkin-' + month_str + '.log', 'a+') as log_f:
        log_f.write(whole_str + '\n')


juzhudi_map = {
    '1-2': '东校区',
    '1-3': '南校区',
    '1-4': '中校区',
    '1-5': '北校区',
    '1-6': '西校区',
    '1-7': '先研院',
    '1-8': '国金院',
    '2-0': '合肥市内校外'
}


# now_status 对应当前状态:
#   1-正常在校园内, 2-正常在家, 3-居家留观, 4-集中留观, 5-住院治疗, 6-其它
# 若地址编号为 340100(合肥), 需添加在校信息：
#   2-东区, 3-南区, 4-中区, 5-北区, 6-西区, 7-先研院, 8-国金院, 9-其他院区, 0-校外
def build_report_form(token, userinfo):
    postcode = userinfo['postcode']
    now_status = userinfo['now_status']
    now_province = postcode[0:2] + '0000'
    now_city = postcode[0:4] + '00'
    now_country = postcode
    if userinfo['now_status'] in juzhudi_map:
        form_dict = {
            '_token': token,
            'juzhudi': juzhudi_map[userinfo['now_status']],
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
            'jinji_lxr': userinfo['emg_name'],
            'jinji_guanxi': userinfo['emg_relation'],
            'jiji_mobile': userinfo['emg_mobile'],
            'other_detail': ''
        }
    else:
        form_dict = {
            '_token': token,
            'now_address': '1',  # 内地
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
            'jinji_lxr': userinfo['emg_name'],
            'jinji_guanxi': userinfo['emg_relation'],
            'jiji_mobile': userinfo['emg_mobile'],
            'other_detail': ''
        }
    form_str = ''
    for k in form_dict.keys():
        form_str = form_str + k + '=' + form_dict[k] + '&'
        if k == 'now_detail' and now_city == '340100':
            form_str = form_str + 'is_inschool=' + now_status.split('-')[1] + '&'
    form_str = form_str[0:-1]
    return form_str


def build_apply_form(info_apply):
    return '_token={0}&start_date={1}&end_date={2}' \
        .format(info_apply['token'], info_apply['start_date'], info_apply['end_date'])


# 自动打卡主程序 成功打卡返回0
def auto_checkin(userinfo):
    print_with_time(userinfo['username'] + ' checkin start')
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
    print1('Getting ' + url + ' ...')
    resp = requests.get(url, headers=header)
    cookies_checkin = update_cookies(cookies_checkin, resp.cookies.get_dict().items())

    url = 'https://weixine.ustc.edu.cn/2020/login'
    print1('Getting ' + url + ' ...')
    resp = requests.get(url, headers=header)
    cookies_checkin = update_cookies(cookies_checkin, resp.cookies.get_dict().items())

    # 修改header
    url = 'https://weixine.ustc.edu.cn/2020/caslogin'
    header['Sec-Fetch-Site'] = 'same-origin'
    header['Referer'] = url
    print1('Getting ' + url + ' ...')
    # 返回302, 禁止自动跳转
    resp = requests.get(url, headers=header, cookies=cookies_checkin, allow_redirects=False)
    cookies_checkin = update_cookies(cookies_checkin, resp.cookies.get_dict().items())

    url = 'https://passport.ustc.edu.cn/login?service=https%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin'
    header['Host'] = 'passport.ustc.edu.cn'
    # header['Sec-Fetch-Site'] = 'same-site'
    print1('Getting ' + url + ' ...')
    resp = requests.get(url, headers=header, allow_redirects=False)
    cookie_dict_passport = {}
    cookie_dict_passport = update_cookies(cookie_dict_passport, resp.cookies.get_dict().items())

    # 创建登录表单 (含验证码识别)
    login_form_str = build_login_form(resp.text, userinfo, cookie_dict_passport['JSESSIONID'],
                                      service='https%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin')

    url = 'https://passport.ustc.edu.cn/login'
    header['Referer'] = 'https://passport.ustc.edu.cn/login?service=https%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin'
    header_post = header.copy()
    header_post['Cache-Control'] = 'max-age=0'
    header_post['Content-Type'] = 'application/x-www-form-urlencoded'
    header_post['Origin'] = 'https://passport.ustc.edu.cn'
    print1('Posting ' + url + ' ...')
    resp = requests.post(url, data=login_form_str, headers=header_post, cookies=cookie_dict_passport,
                         allow_redirects=False)
    # response 302, header的location项中含名为ticket的token, 和 weixine 下的 cookie 一起提交完成身份验证
    try:
        url = resp.headers['location']
        if re.search(r'ticket=ST', url) is None:
            raise BaseException('cannot get CAS-ticket')
    except BaseException as e:
        print_with_time('{0} authentication failed'.format(userinfo['username']))
        print1(e)
        return 1
    print_with_time('{0} authentication success'.format(userinfo['username']))

    header['Host'] = 'weixine.ustc.edu.cn'
    header['Sec-Fetch-Site'] = 'same-site'
    header['Cache-Control'] = 'max-age=0'
    header['Referer'] = 'https://passport.ustc.edu.cn/login'
    print1('Getting ' + url + ' ...')
    resp = requests.get(url, headers=header, cookies=cookies_checkin, allow_redirects=False)
    cookies_checkin = update_cookies(cookies_checkin, resp.cookies.get_dict().items())

    url = 'https://weixine.ustc.edu.cn/2020/caslogin'
    print1('Getting ' + url + ' ...')
    resp = requests.get(url, headers=header, cookies=cookies_checkin, allow_redirects=False)
    cookies_checkin = update_cookies(cookies_checkin, resp.cookies.get_dict().items())

    url = 'https://weixine.ustc.edu.cn/2020/'
    header.pop('Referer')
    print1('Getting ' + url + ' ...')
    resp = requests.get(url, headers=header, cookies=cookies_checkin, allow_redirects=False)
    cookies_checkin = update_cookies(cookies_checkin, resp.cookies.get_dict().items())

    url = 'https://weixine.ustc.edu.cn/2020/home'
    header['Sec-Fetch-Site'] = 'cross-site'
    print1('Getting ' + url + ' ...')
    resp = requests.get(url, headers=header, cookies=cookies_checkin, allow_redirects=False)
    cookies_checkin = update_cookies(cookies_checkin, resp.cookies.get_dict().items())

    # 验证是否获取到身份验证页面
    if resp.status_code != 200:
        print_with_time(userinfo['username'] + ' cannot get to login page')
        return 'failed'

    # 获取页面 form 中 x_csrf_token 等相关信息
    info = parse_checkin_info(resp.text)
    # print_with_time('{0} last check in : {1}, token : {2}'.format(info['uid'], info['time'], info['token']))

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
    print1('Ajax ' + url + ' ...')
    resp = requests.post(url, headers=header_ajax, cookies=cookies_checkin)
    cookies_checkin = update_cookies(cookies_checkin, resp.cookies.get_dict().items())

    url = 'https://weixine.ustc.edu.cn/2020/get_city/' + userinfo['postcode'][0:2] + '0000'
    print1('Ajax ' + url + ' ...')
    resp = requests.post(url, headers=header_ajax, cookies=cookies_checkin)
    cookies_checkin = update_cookies(cookies_checkin, resp.cookies.get_dict().items())

    # 提交 daily_report
    # 是的没有拼错 daliy_report, :-)
    url = 'https://weixine.ustc.edu.cn/2020/daliy_report'
    header['Sec-Fetch-Site'] = 'same-origin'
    header_report = header.copy()
    header_report['Referer'] = 'https://weixine.ustc.edu.cn/2020/home'
    header_report['Origin'] = 'https://weixine.ustc.edu.cn'
    header_report['Content-Type'] = 'application/x-www-form-urlencoded'
    # 填写表单 data
    report_data = build_report_form(info['token'], userinfo)
    print1('Posting ' + url + ' ...')
    resp = requests.post(url, data=report_data.encode('utf-8'), headers=header_report, cookies=cookies_checkin,
                         allow_redirects=False)
    cookies_checkin = update_cookies(cookies_checkin, resp.cookies.get_dict().items())

    url = 'https://weixine.ustc.edu.cn/2020/home'
    header['Referer'] = 'https://weixine.ustc.edu.cn/2020/home'
    print1('Getting ' + url + ' ...')
    resp = requests.get(url, headers=header, cookies=cookies_checkin, allow_redirects=False)
    cookies_checkin = update_cookies(cookies_checkin, resp.cookies.get_dict().items())
    info = parse_checkin_info(resp.text)

    print_with_time('{0} checkin finished'.format(userinfo['username']))
    print_with_time('{0} last check in : {1}'.format(info['uid'], info['time']))

    # 出校报备
    '''
    if userinfo['last_apply'] != '':
        ds = userinfo['last_apply']
        day_last = datetime.datetime(int(ds[0:4]), int(ds[4:6]), int(ds[6:8]))
        delta = datetime.datetime.now() - day_last
        if delta >= 0:
            print_with_time('{0} need apply post'.format(userinfo['username']))
            # 获取报备页面
            url = 'https://weixine.ustc.edu.cn/2020/apply/daliy'
            print1('Getting ' + url + ' ...')
            resp = requests.get(url, headers=header, cookies=cookies_checkin, allow_redirects=False)
            cookies_checkin = update_cookies(cookies_checkin, resp.cookies.get_dict().items())
            info_apply = parse_apply_info(resp.text)
            # 确定页面状态可以报备
            if info_apply is None:
                print_with_time('{0} parse html error'.format(userinfo['username']))
            elif not info_apply['is_able_apply']:
                print_with_time('{0} is not able to apply'.format(userinfo['username']))
            else:
                # 提交报备post
                url = 'https://weixine.ustc.edu.cn/2020/apply/daily/post'
                header_apply = header.copy()
                header_apply['Referer'] = 'https://weixine.ustc.edu.cn/2020/apply/daliy'
                header_apply['Origin'] = 'https://weixine.ustc.edu.cn'
                header_apply['Content-Type'] = 'application/x-www-form-urlencoded'
                apply_data = build_apply_form(info_apply)
                print1('Posting ' + url + ' ...')
                resp = requests.post(url, data=apply_data, headers=header_apply,
                                     cookies=cookies_checkin, allow_redirects=False)
                cookies_checkin = update_cookies(cookies_checkin, resp.cookies.get_dict().items())
                try:
                    if resp.headers['location'] == 'https://weixine.ustc.edu.cn/2020/apply_total?t=d':
                        print_with_time('{0} apply success, authorization due : {1}'
                                        .format(userinfo['username'], info_apply['end_date']))
                    else:
                        raise ValueError
                except BaseException:
                    print_with_time('{0} apply failed'.format(userinfo['username']))
        else:
            print_with_time('{0} not need apply post'.format(userinfo['username']))
'''

    return 0


if __name__ == '__main__':
    path = 'keys.txt'

    if len(sys.argv) > 1:
        try:
            opts, args = getopt.getopt(sys.argv[1:], '-i:-u:', 'idx=')
        except getopt.GetoptError:
            print('input args error: auto.py -i <user index>')
            sys.exit(2)
        for opt, arg in opts:
            if opt in ('-i', '--idx'):
                i = int(arg)
                users = load_users(path)
                print_with_time(str(len(users)) + ' user(s) found in ' + path)
                exit(auto_checkin(users[i]))
            if opt in ('-u'):
                bs = bytes(arg.encode('utf-8'))
                info_str = str(base64.b64decode(bs), encoding='utf-8')
                exit(auto_checkin(parse_info_str(info_str)))

    else:
        users = load_users(path)
        print_with_time(str(len(users)) + ' user(s) found in ' + path)
        time.sleep(random.randint(5, 30))
        for i in range(len(users)):
            auto_checkin(users[i])
            if i < len(users) - 1:
                time.sleep(random.randint(30, 90))
