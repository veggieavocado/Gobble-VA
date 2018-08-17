# -*- coding: utf-8 -*-
"""
Created on Fri Aug 17 05:15:30 2018

@author: LeeMH
"""
from bs4 import BeautifulSoup
from datetime import datetime
import requests

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

if PRODUCTION == True:
    all_title = NaverContent.objects.using('contents').filter(data_type="R").values_list('title')
    CHECKLIST = [a[0] for a in all_title]
elif PRODUCTION == False:
    all_title = NaverContent.objects.filter(data_type="R").values_list('title')
    CHECKLIST = [a[0] for a in all_title]

# init
class NaverRealtimeCrawler(object):
    '''
    네이버 증권 실시간 속보 크롤러
    '''
    def __init__(self):
        self.today = datetime.today().strftime('%Y%m%d')
        self.fin_nhn = 'https://finance.naver.com/{}'
        self.main_today = datetime.today().strftime('%Y-%m-%d')
        self.main_news = 'https://finance.naver.com/news/mainnews.nhn?date={}'
        self.real_time_list = 'https://finance.naver.com/news/news_list.nhn?mode=LSS2D&section_id=101&section_id2=258&date={}&page={}'
        self.user_agent = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'}
        print("NAVER CRAWLER READY!")

    def request_get(self, url, user_agent):
        req = requests.get(url, headers= user_agent, auth=('user', 'pass'))
        return req

    def html_parser(self, req):
        soup = BeautifulSoup(req.text, 'html.parser')
        return soup
    # find & findall
    def soup_find(self, soup, tags, class_dict=None, func=None):
        if func == 'all':
            source = soup.findAll(tags, class_dict)
        elif func == None:
            source = soup.find(tags, class_dict)
        return source

    @timeit
    def get_realtimenews_url(self):
        req = self.request_get(self.real_time_list.format(self.today, 1), self.user_agent)
        soup = self.html_parser(req)
        pgRR = self.soup_find(soup, 'td', {'class':'pgRR'})
        last_page = self.soup_find(pgRR, 'a')['href'][-2:]

        url_title_data = []
        for i in range(1,int(last_page)):
            req = self.request_get(self.real_time_list.format(self.today, i), self.user_agent)
            sub_soup = self.html_parser(req)
            sub_title_dd = self.soup_find(sub_soup, 'dd', {'class':'articleSubject'}, func='all')
            sub_title_dt = self.soup_find(sub_soup, 'dt', {'class':'articleSubject'}, func='all')
            url_title_data += sub_title_dd
            url_title_data += sub_title_dt
        print(len(url_title_data))
        real_time_url = [self.soup_find(sub, 'a')['href'].replace('§', '&sect') for sub in url_title_data]
        return real_time_url

    @timeit
    def get_data(self, url_list, checklist):
        url_list = url_list
        data_list = []
        for url in url_list:
            self.req = self.request_get(self.fin_nhn.format(url), self.user_agent)
            soup = self.html_parser(self.req)
            url = self.fin_nhn.format(url)
            title = self.soup_find(soup, 'h3').text.replace('\n','').replace('\t','').strip()
            upload_time = self.soup_find(soup, 'span', {'class':'article_date'}).text
            if title in checklist:
                print('Already up-to-date.')
                continue
            media = self.soup_find(soup, 'span', {'class':'press'}).img['title']
            data_dict = {'title':title, 'media':media, 'url':url, 'data_type':'R', 'upload_time': upload_time}
            data_list.append(data_dict)
        print(len(data_list))
        return data_list


def NaverDataSend():
    nrt = NaverRealtimeCrawler()
    nrt_url = nrt.get_realtimenews_url()
    nrt_data = nrt.get_data(nrt_url, CHECKLIST)
    if len(nrt_data) == 0:
        print('Already up-to-date.')
    else:
        for nrt_part in nrt_data:
            title = nrt_part['title']
            url = nrt_part['url']
            upload_time = nrt_part['upload_time']
            media = nrt_part['media']
            data_type = nrt_part['data_type']
            naver_content_orm = NaverContent(title=title, url=url, upload_time=upload_time,\
                                            media=media, data_type=data_type)
            naver_content_orm.save()
        print('DB Send Success')
