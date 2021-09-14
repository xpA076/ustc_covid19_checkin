from download_code import download_img
from predict_vcode import predict

from bs4 import BeautifulSoup
import re


def get_form_token(html_text):
    re_input = re.search(r'<\s*input[^>]*token[^>]*>', html_text)
    input_text = html_text[re_input.span()[0]: re_input.span()[1]]
    re_value = re.search(r'value="\w*"', input_text)
    token = input_text[re_value.span()[0] + 7: re_value.span()[1] - 1]
    return token


def get_info(html_text):
    bs_text = html_text.replace('</br>', '').replace('<br/>', '')
    try:
        bs = BeautifulSoup(bs_text, features="html.parser")
        forms = bs.find_all(name='form')
        token = forms[0].find_all('input', {'name': '_token'})[0]['value']
        time = forms[0].find_all('strong')[1].text[8:27]
        name = forms[1].find('input', {'name': 'name'})['value']
        uid = forms[1].find('input', {'name': 'xuegonghao'})['value']
        phone_num = forms[1].find('input', {'name': 'mobile'})['value']
        return {
            'token': token,
            'time': time,
            'name': name,
            'uid': uid,
            'phone_num': phone_num
        }
    except BaseException:
        return None


def get_login_info(html_text):
    bs_text = html_text.replace('</br>', '').replace('<br/>', '')
    try:
        bs = BeautifulSoup(bs_text, features="html.parser")
        # vcode = bs.find(id='validate')
        cas_lt = bs.find('input', {'name': 'CAS_LT'})['value']
        show_code = bs.find('input', {'name': 'showCode'})['value']
        if show_code is None:
            show_code = ''
        # button = bs.find('input', {'name': 'button'})
        return {
            'cas_lt': cas_lt,
            'show_code': show_code,
        }
    except BaseException:
        return None


def build_login_form(html_text, userinfo, session_id):
    info = get_login_info(html_text)
    form_dict = {
        'model': 'uplogin.jsp',
        'CAS_LT': info['cas_lt'],
        'service': 'https%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin',
        'warn': '',
        'showCode': info['show_code'],
        'username': userinfo['username'],
        'password': userinfo['password'],
        # 'button': ''
    }
    form_str = ''
    for k in form_dict.keys():
        form_str = form_str + k + '=' + form_dict[k] + '&'
    if info['show_code'] == '1':
        print('require vcode ...')
        download_img('temp.jfif', session_id)
        ans = predict('temp.jfif', 'nn_data', 'nn1')
        form_str = form_str + 'validate={0}{1}{2}{3}&'.format(ans[0], ans[1], ans[2], ans[3])
        print('predict vcode as : ' + str(ans))
    form_str += 'button='
    return form_str


if __name__ == '__main__':
    with open('1.html', 'r', encoding='utf-8') as f:
        text = f.read()
    a = get_login_info(text)
    get_info(text.replace('</br>', '').replace('<br/>', ''))
    # get_info('<div><div id="user_info">123</div></div>')
