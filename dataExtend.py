'''
Descripttion: 
version: 
Author: Six
Date: 2021-06-06 15:21:17
LastEditors: Six
LastEditTime: 2021-06-07 10:33:28
'''

"""
获取新的数据，主要针对Alexa排名进行实际站点数据的扩增
扩增包括两个部分
一是通过搜索域名，获取搜索结果链接
二是通过访问获取页面上的链接

以上两个方面的链接都需要进行进一步处理，以去除无效和重复的链接
"""

import requests
from lxml import etree

from utils import getFQDN,baiduResult,validURL

def pageExtend(url):
    proxies = {
        "https":"https://127.0.0.1:1080",
        "http":"http://127.0.0.1:1080"
    }
    try:
        urls = []
        res = requests.get(url,timeout=20,proxies=proxies)
        if res.status_code==200:
            pdom = etree.HTML(res.text)
            if pdom:
                urls = pdom.xpath("//*/a/@href")
                urls = [url for url in set(urls) if url.startswith("//") or (not url.startswith("/") and not url.startswith("java"))]
        return urls
    except Exception as e:
        print(e)
        return []

def searchExtend(url):
    results = []
    _,domain,suffix,_ = getFQDN(url)
    keywords = [domain+"."+suffix]
    print(keywords)
    try:
        snum,results = baiduResult(keywords)
    except Exception as e:
        print(e)
    return results


