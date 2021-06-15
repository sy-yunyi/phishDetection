'''
Descripttion: 
version: 
Author: Six
Date: 2021-06-14 20:34:22
LastEditors: Six
LastEditTime: 2021-06-14 22:13:43
'''
import requests
import configparser


def hhpSearchGoogle(keywords):
    config = configparser.ConfigParser()
    config.read('conf\project.conf')
    api_key = config["googleapi"]["key"]
    api_cx = config["googleapi"]["cx"]
    url = r"https://customsearch.googleapis.com/customsearch/v1?key={key}&q={st}&cx={cx}".format(key=api_key,st="%20".join(keywords),cx=api_cx)
    proxies = {
    "https": "https://127.0.0.1:1080",
    "http": "http://127.0.0.1:1080"
            }
    search_links = []
    try:
        res = requests.get(url,proxies=proxies,timeout=10)
        if res.status_code==200:
            snums = res.json()["searchInformation"]["totalResults"]
            for li in res.json()["items"]:
                search_links.append(li["link"])
        return snums,search_links
    except Exception as e:
        print(e)
        return 0,[]

snums, links = hhpSearchGoogle(["site:qq.com","inurl:login"])
print(snums)
print(links)