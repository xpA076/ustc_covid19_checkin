from html_parser import *
from bs4 import BeautifulSoup

with open('1.txt', 'r', encoding='utf-8') as r:
    s = r.read()
    bs_text = s.replace('</br>', '').replace('<br/>', '')
    try:
        bs = BeautifulSoup(bs_text, features="html.parser")
        forms = bs.find_all(name='form')
        token = forms[0].find_all('input', {'name': '_token'})[0]['value']
        start_date = forms[0].find_all('input', {'name': 'start_date'})[0]['value']
        end_date = forms[0].find_all('input', {'name': 'end_date'})[0]['value']
        ps = bs.find_all('p')
        l = len(ps)
        for p in ps:
            #p = ps[i]
            tx = p.text
            if '你的当前状态：在校已出校报备' in tx:
                a = 2
            else:
                a = 3


        a = 1

    except BaseException:
        pass


