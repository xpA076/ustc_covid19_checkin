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




if __name__ == '__main__':
    print(get_info('123'))
    with open('1.html', 'r') as f:
        text = f.read()
    get_info(text.replace('</br>', '').replace('<br/>', ''))
    #get_info('<div><div id="user_info">123</div></div>')


