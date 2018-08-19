# -*- coding: utf-8 -*-
"""
Created on Fri Aug 17 05:15:30 2018

@author: LeeMH
"""
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

TODAY = datetime.today().strftime("%Y-%m-%d")

TODAY = datetime.today() - timedelta(days=1)
TODAY = TODAY.strftime("%Y-%m-%d")

if PRODUCTION == True:
    all_title = NaverContent.objects.using('contents').filter(data_type="R").filter(upload_time__contains=TODAY).values_list('title')
    CHECKLIST = [a[0] for a in all_title]
elif PRODUCTION == False:
    all_title = NaverContent.objects.filter(data_type="R").filter(upload_time__contains=TODAY).values_list('title')
    CHECKLIST = [a[0] for a in all_title]

from gobble.module.crawler import Crawler

class NaverRealtimeCrawler(Crawler):
    '''
    네이버 증권 실시간 속보 크롤러
    '''
    def __init__(self):
        super().__init__()

    @timeit
    def get_realtimenews_url(self, func):
        req = self.request_get(self.real_time_list.format(self.rt_today, 1), self.user_agent)
        soup = self.html_parser(req)
        url_list = []
        if func == 'new':
            url_data = self.find_navernews_url(soup, url_list)

        elif func == 'all':
            pgRR = self.soup_find(soup, 'td', {'class':'pgRR'})
            last_page = self.soup_find(pgRR, 'a')['href'][-3:]
            last_page = re.findall("\d+", last_page)[0]

            sub_list = []
            for i in range(1,int(last_page)+1):
                req = self.request_get(self.real_time_list.format(self.rt_today, i), self.user_agent)
                sub_soup = self.html_parser(req)
                url_list += self.find_navernews_url(sub_soup, sub_list)
            url_data = url_list
        else:
            print("Choose between 'all' and 'new'")
        url_data = list(set(url_data))
        print(len(url_data))
        real_time_url = [self.soup_find(sub, 'a')['href'].replace('§', '&sect') for sub in url_data]
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


def NaverDataSend(func):
    nrt = NaverRealtimeCrawler()
    if func == 'new':
        nrt_url = nrt.get_realtimenews_url('new')
    else:
        nrt_url = nrt.get_realtimenews_url('all')
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
