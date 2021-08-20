from re import search
import requests
from requests.api import get
from utils import extractTitle,getFQDN,searchData,pathDomain,googleResult
from lxml import etree
import hashlib
import redis
import json


pool = redis.ConnectionPool(host="127.0.0.1",port=6379,db=1,password="si1ex")
# type 为file 和url ，url 表示需要主动请求获取页面数据，file 则为输入为页面文件，直接进行解析
def LDP(url,path = None,type="URL"):
    """
    实现钓鱼检测方法LDP
    1. 提取URL域名（顶级域），页面标题
    2. 检查域名是否在安全列表中
    3. 域名 + 标题作为搜索字符串进行搜索，提取前6搜索结果中的域名
    4. 判定搜索结果中的域名是否命中，命中则判定为正常域名，否则为钓鱼域名
    """
    if type=="URL":
        res = requests.get(url)
    else:
        with open(path,"rb") as fp:
            res = fp.read()
    title = extractTitle(res,type=type)
    _,domain,suffix,fqdn = getFQDN(url)
    keywords = [domain+"."+suffix,title]
    res_id = hashlib.md5((url+"-".join(keywords)).encode()).hexdigest()
    # status_code,results = searchData(res_id)
    resdb = redis.Redis(connection_pool=pool)
    if not resdb.get(res_id):
        try:
            snums,results = googleResult(keywords)
        except Exception as e:
            raise(e)
        # searchData(res_id,results=results)
        resdb.set(res_id,json.dumps({"links":results,"lnum":snums}))
    else:
        sdata = json.loads(resdb.get(res_id))
        results = sdata["links"]
        snums = sdata["lnum"]

    if len(results)>=6:
        results = results[:6]
    pUrl,pDomain,pFqdn = pathDomain(url,domain,fqdn,results)
    if pDomain:
        return 0
    else:
        return 1