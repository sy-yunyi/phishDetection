'''
Descripttion: 
version: 
Author: Six
Date: 2021-06-06 19:02:42
LastEditors: Six
LastEditTime: 2021-06-16 21:56:34
'''

from pdb import main
import pandas as pd
import logging
import logging.config
import queue

from utils import validURL
from dataExtend import pageExtend,searchExtend
from hhpImp import H2Phish

# 数据扩增
logging.config.fileConfig("logging.conf")
# logger = logging.getLogger("dataExtend")
# logger.info("开始扩增数据...")
org_domain = pd.read_csv(r"F:\loading\phish\钓鱼检测方案二\code\data\Alexa-top-1m.csv",names=[0,1])[1].values[:10000]
# for di in org_domain:
#     url = validURL(di)
#     # page_urls = pageExtend(url)
#     page_urls = searchExtend(url)
#     logger.info("扩增数量："+str(len(page_urls))+", "+url)
#     with open("data/searchExtendURL.txt","a+",encoding="utf-8") as fp:
#         for pi in page_urls:
#             fp.write(pi+"\n")

# logger.info("扩增数据结束...")

# with open(r"F:\phishDetection\raw_data\pageExtendURL.txt","r",encoding="utf-8") as fp:
#     lines = fp.readlines()
#     org_domain = [line.strip() for line in lines]

# org_domain = ["https://www.st.com/zh/ecosystems/aliyun.html"]

logger = logging.getLogger("hhp")
logger.info("detection start...")
domian_queue = queue.Queue()
for di in org_domain:
    domian_queue.put(di)
results = []
while not domian_queue.empty():
    url = domian_queue.get()
    url = validURL(url)
    try:
        dre = H2Phish(url)
        results.append(dre)
        if dre != 0:
            logger.info(str(dre)+" - "+url)
    except Exception as e:
        if e.__str__()=="未获取到页面信息":
            domian_queue.put(url)
            logger.info("429"+" - "+url)
        else:
            print(e)
            logger.info("失败"+" - "+url)
with open("data/hhp_searchExtendURL_0616.txt","w",encoding="utf-8") as fp:
    for ri in results:
        fp.write(str(ri)+"\n")
logger.info("detection end...")