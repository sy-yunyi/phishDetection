'''
Descripttion: 
version: 
Author: Six
Date: 2021-06-05 14:43:47
LastEditors: Six
LastEditTime: 2021-06-05 21:20:13
'''
import logging
import logging.config
from os import path
import requests
import queue

from utils import getFQDN,baiduResult

logging.config.fileConfig("logging.conf")
logger = logging.getLogger("hhp")

# logger.info("info message")



def isRedirection(url:str):
    """
    对url重定向情况进行判定。
    非重定向 - > 0 , url, rcode
    重定向 - >   1 , 重定向后的URL, rcode
    无法判定 - > 2 , url, 0
    """
    proxies = {
        "https":"https://127.0.0.1:1080",
        "http":"http://127.0.0.1:1080"
    }
    try:
        res = requests.get(url,proxies=proxies,timeout=20,verify=False)
        _,bdoamin,_,_ = getFQDN(url)
        if url != res.url:
            _,rdomain,_,_ = getFQDN(res.url)
            # 同站点间的跳转，不记录
            if bdoamin != rdomain:
                return 1, res.url,res.status_code
        elif len(res.history) >0 and (url != res.history[-1].url):
            _,rhdomain,_,_ = getFQDN(res.history[-1].url)
            if bdoamin != rhdomain:
                return 1, res.history[-1].url,res.status_code
        else:
            return 0,url,res.status_code
    except Exception as e:
        logger.info("{}，重定向情况无法判定。".format(url))
        logger.info(e.__str__())
        return 2,url,0

def spGenerate(url):
    """
    搜索模式生成
    """
    _,_,_,fqdn = getFQDN(url)
    url = url.split("?")[0] # 参数分割
    url = url.split("#")[0] # 锚点分割
    url = url.split("/")
    if ":" in url[2]:
        url[2] = url[2].split(":")[0]
    findex = url.index(fqdn)
    if len(url) == findex+1 or (len(url) == findex+2 and url[findex+1]==""):
        return fqdn,""
    else:
        return fqdn,url[findex+1]

def resourceStrategy(url,results):
    _,_,_,fqdn = getFQDN(url)
    url = url.split("?")[0] # 参数分割
    url = url.split("#")[0] # 锚点分割
    url = url.split("/")
    if ":" in url[2]:  # 去除端口号
        url[2] = url[2].split(":")[0]
    if url[-1]=="":
        url=url[:-1]
    findex = url.index(fqdn)
    url = url[findex:]
    
    if "." in url[-1]:
        file_type = url[-1].split(".")[-1]
    ftc = 0

    if len(url) == 1 or (len(url)==2 and url[1]==""):
        return 0,0,0   # 资源策略是否有效，资源类型一致性，资源路径相似性
    else:
        paths = []
        for ri in results:
            _,_,_,rfqdn = getFQDN(ri)
            tmp = ri.split("?")[0].split("#")[0].split("/")
            if ":" in tmp[2]:
                tmp[2] = tmp[2].split(":")[0]
            rpath = tmp[tmp.index(rfqdn):]
            if rpath[-1].split(".")[-1] == file_type:
                ftc += 1
            paths.append(len(set(url[1:]).intersection(set(rpath[1:]))) / (len(rpath[1:])+1))
    return 1, ftc / (len(results)+1) , sum(paths > 0.5) / len(url[1:])

def H2Phish(urls: queue) -> list:
    logger.info("开始执行...")

    while urls.Empty():
        url = urls.get()
        isre, re_url,rcode = isRedirection(url)
        fqdn_old,start_old = spGenerate(url)
        if start_old!="":
            keywords = ["site:"+fqdn_old,"inurl:"+start_old]
        else:
            keywords = ["site:"+fqdn_old]
            snum_old,results_old = baiduResult(keywords)
        
        # 对重定向的处理
        if isre:
            fqdn_re,start_re= spGenerate(re_url)
            if start_re!="":
                keywords = ["site:"+fqdn_re,"inurl:"+start_re]
            else:
                keywords = ["site:"+fqdn_re]
            snum_re,results_re = baiduResult(keywords)

            # 索引策略
            if snum_old / (snum_re+1) > 50 :
                return 1  # 重定向钓鱼
            elif snum_old ==0 or snum_re ==0:
                return 2 # 普通钓鱼
        else:
            # 资源策略
            isver,ftscore,rscore = resourceStrategy(url,results_old)
            if isver:
                if ftscore == 0:
                    return 3 # 对于无法获取页面的站点，其文件类型存在异常，可能为挂马，判定为钓鱼
                if rscore < 0.25 * len(results_old):
                    return 4 # 
            else:
                return 0  # 正常

        


