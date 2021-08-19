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
import time
import threading
from utils import validURL
from dataExtend import pageExtend,searchExtend
from hhpImp import H2Phish



def detect_exec(data_queue):
    data_path = r"F:\研究方案\钓鱼检测框架-PhishTotal\Phishpedia\benign_sample_30k"
    while(not data_queue.empty()):
        item = data_queue.get()
        url,dir = item[1],item[0]
        link_nums = 0
        if type(url)!=str:
            continue
        url = validURL(url)
        fp_pre = open(r"data\hhp_normal.txt","a+")
        if url in open(r"G:\bak\hp-f\phishDetection\data\hhp_normal.txt","r",encoding="ISO-8859-1").read():
            print("have done\n")
            continue
        try:
            dir.replace("<token>",",")
            url.replace("<token>",",")
            print(url)
            # print(LDP(ui,os.path.join(os.path.join(data_path,di),"html.txt"),type="file"))
            # res = jailPhish(url,os.path.join(os.path.join(data_path,dir),"html.txt"),type="file")
            res,link_nums = H2Phish(url)
            fp_pre.write(url+"\t"+dir+"\t"+str(res)+"\t"+str(link_nums)+"\t"+"detection"+"\n")
        except Exception as e:
            if e.__str__()=="未获取到页面信息":
                domian_queue.put(url)
                time.sleep(5)
            else:
                print(e)
                # 搜索引擎屏蔽
            fp_pre.write(url+"\t"+dir+"\t"+str(10)+"\t"+str(link_nums)+"\t"+str(e)+"\n")
        fp_pre.close()
def test():
    # 数据扩增
    logging.config.fileConfig("logging.conf")
    # logger = logging.getLogger("dataExtend")
    # logger.info("开始扩增数据...")
    org_domain = pd.read_csv(r"raw_data\Alexa-top-1m.csv",names=[0,1])[1].values[:10000]
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

def getTestData():
    file_path = r"G:\bak\hp-f\phishDetection\data\normal_final.csv"
    df = pd.read_csv(file_path)
    return df['dir'].values,df['url'].values

def detecTheads(detection,NUM,dataq):
    t_list = []
    for i in range(NUM):
        t = threading.Thread(target=detection, args=(dataq,))
        t.start()
        t_list.append(t)
    
    for ti in t_list:
        ti.join()

if __name__=="__main__":
    # logging.config.fileConfig("logging.conf")
    # logger = logging.getLogger("hhp")
    # logger.info("detection start...")

    domian_queue = queue.Queue()
    file_dirs,file_urls = getTestData()
    for di,ui in zip(file_dirs,file_urls):
        domian_queue.put([di,ui])
    NUM = 1
    detecTheads(detect_exec,NUM,domian_queue)


    
