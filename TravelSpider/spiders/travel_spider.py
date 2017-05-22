#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import scrapy
from TravelSpider.items import TravelspiderItem
import requests
from bs4 import BeautifulSoup
import json


class TravelSpider(scrapy.Spider):
    name = 'travel'
    allowed_domains = ['ly.com']
    start_urls = []

    attempt = requests.get(u'http://www.ly.com/travels/travel/getSearchYouJiList?k=北京&pindex=1&psize=100').json()
    for index in range(1, int(attempt['pageCount']) + 1):
        result = requests.get(u'http://www.ly.com/travels/travel/getSearchYouJiList?k=北京&pindex='
                              + str(index) + '&psize=100').json()
        youji_list = result['youJiList']
        if youji_list:
            start_urls += ['http://www.ly.com/travels/' + youji['travelNoteId'] + '.html' for youji in youji_list]

    def parse(self, response):
        # Scrapy 中的 XPath 解析方法，'scrapy crawl travel -o youji.json' 即可直接存储
        # item = TravelspiderItem()
        # item['url'] = response.url
        # item['desc'] = response.xpath("//p[contains(@id, 'txt')]/text()").extract()
        # item['imgs'] = response.xpath('//img/@data-img-src').extract()
        # yield item

        # 为了保存内容中文字和图片的相对位置信息，使用 BeautifulSoup 从头到尾解析了一遍
        youji = {}
        soup = BeautifulSoup(response.body)
        youji['title'] = soup.h1.em.string
        youji['url'] = response.url
        youji['channel'] = '同程'
        youji['much'] = soup.find('span', class_='mainLeft-rmb').em.string.replace('-', '')
        youji['who'] = soup.find('span', class_='mainLeft-people').em.string.replace('-', '')
        youji['days'] = soup.find('span', class_='mainLeft-day').em.string.replace('-', '')
        youji['how'] = soup.find('span', class_='mainLeft-way').em.string.replace('-', '')
        youji['travel_time'] = ''
        youji['create_time'] = soup.find('span', class_='createTime').em.string.split()[0].replace('.', '-')

        content = ''
        divs = soup.find('div', class_='contentall').find_all('div', recursive=False)
        h2 = ''
        for div in divs:
            if 'dayHeadBg' in div['class']:
                content += '<h1>' + div.div.label.string + '</h1>'
            elif 'mainDayTitle' in div['class']:
                h2 = div.find('div', class_='tt te').label.string
                content += '<h2>' + h2 + '</h2>'
            elif 'content' in div['class']:
                medias = div.find_all(['img', 'p'])
                for media in medias:
                    if media.name == 'img':
                        content += '<img src="' + media['data-img-src'] + '" title="【' + h2 + '】"/>'
                    elif media.name == 'p':
                        content += '<p>' + media.string + '</p>'
        youji['content'] = content

        filename = 'tongcheng-' + response.url.split('/')[-1].replace('html', 'txt')
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(json.dumps(youji, ensure_ascii=False))
