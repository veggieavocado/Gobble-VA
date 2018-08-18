from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import requests
import re

from utils.processor_checker import timeit

import os, sys, glob
from molecular.settings import PRODUCTION

start_path = os.getcwd()
proj_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "molecular.settings")
sys.path.append(proj_path)
os.chdir(proj_path)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from contents.models import NaverContent
from gobble.module.crawler import Crawler


TODAY = datetime.today().strftime("%Y-%m-%d")
TODAY = datetime.today() - timedelta(days=1)
TODAY = TODAY.strftime("%Y-%m-%d")

if PRODUCTION == True:
    all_title = NaverContent.objects.using('contents').filter(data_type="M").filter(upload_time__contains=TODAY).values_list('title')
    CHECKLIST = [a[0] for a in all_title]
elif PRODUCTION == False:
    all_title = NaverContent.objects.filter(data_type="R").filter(upload_time__contains=TODAY).values_list('title')
    CHECKLIST = [a[0] for a in all_title]


class NaverMajorCrawler(Crawler):
    '''
    네이버 증권 실시간 속보 크롤러
    '''
    def __init__(self):
        super().__init__()

    @timeit
    def url_get(self):
        req = self.request_get(self.main_news.format(self.main_today, 1), self.user_agent)
        soup = self.html_parser(req)
        pgRR = self.soup_find(soup, 'td', {'class':'pgRR'})
        last_page = self.soup_find(pgRR, 'a')['href'][-3:]
        last_page = re.findall("\d+", last_page)[0]

        url_title_data = []
        for i in range(1,int(last_page)):
            req = self.request_get(self.main_news.format(self.main_today, i), self.user_agent)
            sub_soup = self.html_parser(req)
            sub_title_dd = self.soup_find(sub_soup, 'dd', {'class':'articleSubject'}, func='all')
            sub_title_dt = self.soup_find(sub_soup, 'dt', {'class':'articleSubject'}, func='all')
            url_title_data += sub_title_dd
            url_title_data += sub_title_dt
        print(len(url_title_data))
        major_new_url = [self.soup_find(sub, 'a')['href'].replace('§', '&sect') for sub in url_title_data]
        return major_new_url

    @timeit
    def get_data(self, url_list, checklist):
        url_list = url_list
        data_list = []
        for url in url_list:
            req = self.request_get(self.fin_nhn.format(url), self.user_agent)
            soup = self.html_parser(req)
            url = self.fin_nhn.format(url)
            title = self.soup_find(soup, 'h3').text.replace('\n','').replace('\t','').strip()
            if title in checklist:
                print('Already up-to-date.')
                continue
            upload_time = self.soup_find(soup, 'span', {'class':'article_date'}).text
            contents = self.soup_find(soup, 'div', {'class':'articleCont'}).text.replace('\n','').replace('\t','').strip()
            media = self.soup_find(soup, 'span', {'class':'press'}).img['title']
            data_dict = {'title':title, 'media':media, 'url':url, 'data_type':'M', 'upload_time': upload_time, 'contents':contents}
            data_list.append(data_dict)
        print(len(data_list))
        return data_list


def NaverDataSend():
    nmt = NaverMajorCrawler()
    nmt_url = nmt.url_get()
    nmt_data = nmt.get_data(nmt_url, CHECKLIST)
    if len(nmt_data) == 0:
        print('Already up-to-date.')
    else:
        for nmt_part in nmt_data:
            title = nmt_part['title']
            url = nmt_part['url']
            upload_time = nmt_part['upload_time']
            media = nmt_part['media']
            data_type = nmt_part['data_type']
            content = nmt_part['contents']
            naver_content_orm = NaverContent(title=title, url=url, upload_time=upload_time,\
                                            media=media, data_type=data_type, content=content)
            naver_content_orm.save()
        print('DB Send Success')
