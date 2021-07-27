'''
Descripttion: 
version: 
Author: Six
Date: 2021-06-05 14:43:47
LastEditors: Six
LastEditTime: 2021-06-16 10:02:03
'''
import logging
import logging.config
from os import path
import requests
import queue
import configparser

from utils import getFQDN,baiduResult, googleResult
from googleAPI import hhpSearchGoogle

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
            else:
                return 0,url,res.status_code
        elif len(res.history) >0 and (url != res.history[-1].url):
            _,rhdomain,_,_ = getFQDN(res.history[-1].url)
            if bdoamin != rhdomain:
                return 1, res.history[-1].url,res.status_code
            else:
                return 0,url,res.status_code
        else:
            return 0,url,res.status_code
    except Exception as e:
        logger.info("{}，重定向情况无法判定。".format(url))
        logger.info(e.__str__())
        return 2,url,0

def isRedirectionV2(url:str):
    """
    对url重定向情况进行判定。 [更新使用head方法，更快进行判定]
    非重定向 - > 0 , url, rcode
    重定向 - >   1 , 重定向后的URL, rcode
    无法判定 - > 2 , url, 0
    """
    proxies = {
        "https":"https://127.0.0.1:1080",
        "http":"http://127.0.0.1:1080"
    }
    try:
        res = requests.head(url,proxies=proxies,timeout=20,verify=False)
        if res.status_code >= 300 and res.status_code <400:
            return 1, res.url,res.status_code
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
    config = configparser.ConfigParser()
    config.read('conf\project.conf')
    file_types = config["filetype"]["types"]
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
    file_type = None
    if "." in url[-1]:
        file_type = url[-1].split(".")[-1]
    ftc = 0

    if len(url) == 1 or (len(url)==2 and url[1]==""): # 没有路径时
        return 0,0,0   # 资源策略是否有效，资源类型一致性，资源路径相似性
    else:
        paths = []
        for ri in results:
            _,_,_,rfqdn = getFQDN(ri)
            tmp = ri.split("?")[0].split("#")[0].split("/")
            if ":" in tmp[2]:
                tmp[2] = tmp[2].split(":")[0]
            rpath = tmp[tmp.index(rfqdn):]
            if file_type and rpath[-1].split(".")[-1] == file_type: 
                ftc += 1
            paths.append(len(set(url[1:]).intersection(set(rpath[1:]))) / (len(rpath[1:])+1))
        if not file_type or file_type not in file_types:
            return 2,0,sum([1 for pi in paths if pi >=0.2]) / len(url[1:])
        else:
            return 1, ftc / (len(results)+1) , sum([1 for pi in paths if pi >= 0.2]) / len(url[1:])

def H2Phish(url:str) -> int:

    isre, re_url,rcode = isRedirection(url)
    fqdn_old,start_old = spGenerate(url)
    if start_old!="":
        keywords = ["site:"+fqdn_old,"inurl:"+start_old]
    else:
        keywords = ["site:"+fqdn_old]
    try:
        # snum_old,results_old = baiduResult(keywords)
        snum_old,results_old = googleResult(keywords)
        # snum_old,results_old = hhpSearchGoogle(keywords)
        snum_old = int(snum_old)
    except Exception as e:
        raise(e)
        # if e.__str__()=="未获取到页面信息":
        #     urls.put(url)
    
    # 对重定向的处理
    if isre==1:
        fqdn_re,start_re= spGenerate(re_url)
        if start_re!="":
            keywords = ["site:"+fqdn_re,"inurl:"+start_re]
        else:
            keywords = ["site:"+fqdn_re]
        try:
            # snum_re,results_re = baiduResult(keywords)
            snum_re,results_re = googleResult(keywords)
            # snum_re,results_re = hhpSearchGoogle(keywords)
            snum_re = int(snum_re)
        except Exception as e:
            print(e)
            raise(e)
        
        # 索引策略
        
        if snum_old / (snum_re+1) > 50 or snum_re / (snum_old+1) > 50:
            return 1  # 重定向钓鱼
        elif snum_old ==0 or snum_re ==0:
            return 2 # 普通钓鱼

    if snum_old ==0:
        return 2 # 普通钓鱼
    if snum_old > 10000:
        return 0
    # 资源策略
    isver,ftscore,rscore = resourceStrategy(url,results_old)
    if isver==1:
        if ftscore == 0:
            return 3 # 对于无法获取页面的站点，其文件类型存在异常，可能为挂马，判定为钓鱼
        if rscore < 0.25 * len(results_old):
            return 4 # 
    elif isver==2 and rscore < 0.25 * len(results_old):
        return 4 # 
    return 0  # 正常

        


