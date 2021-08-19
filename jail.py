import requests
from utils import getFQDN,extractTitle,searchData,googleResult,pathDomain,extractURL
import hashlib


def jailJudge(url,path,results,type="URL"):
    proxies = {
    "https": "http://127.0.0.1:1080",
    "http": "http://127.0.0.1:1080"
            }
    if type=="URL":
        res = requests.get(url)
    else:
        with open(path,"rb") as fp:
            res = fp.read()
    a_link,style_link,js_link,image_link = extractURL(res,type=type)
    query_a_link = []
    query_style_link = []
    query_js_link = []
    query_image_link = []
    for ri in results:
        try:
            res_id2 = hashlib.md5((ri+url).encode()).hexdigest()
            status_code,results = searchData(res_id2)
            if status_code==0:
                res_u = requests.get(ri,proxies=proxies)
                au_link,styleu_link,jsu_link,imageu_link = extractURL(res_u,type="URL")
                searchData(res_id2,[au_link,styleu_link,jsu_link,imageu_link])
            else:
                au_link,styleu_link,jsu_link,imageu_link =results[0],results[1],results[2],results[3]
            query_a_link.extend(au_link)
            query_style_link.extend(styleu_link)
            query_js_link.extend(jsu_link)
            query_image_link.extend(imageu_link)
        except Exception as e:
            print(e)
    DURLs = set(a_link+style_link+js_link+image_link)
    QURLs = set(query_a_link+query_style_link+query_js_link+query_image_link)
    jdq = len(DURLs.intersection(QURLs)) / (len(DURLs)+len(QURLs) - len(DURLs.intersection(QURLs)) + 1)
    return jdq


def jailPhish(url,path=None,type="URL"):
    """
    1. 提取域名和标题
    2. 生成搜索字符串，域名+标题 / 域名
    3. 搜索，取前10结果，如果同时命中域名和URL，则直接判定为正常；如果仅命中域名，则进行相似计算，大于阈值则判定为正常；否则为钓鱼
    """
    if type=="URL":
        res = requests.get(url)
    else:
        with open(path,"rb") as fp:
            res = fp.read()
    title = extractTitle(res,type="file")
    _,domain,suffix,fqdn = getFQDN(url)
    keywords = [domain+"."+suffix,title]
    res_id = hashlib.md5((url+"-".join(keywords)).encode()).hexdigest()
    status_code,results = searchData(res_id)
    if status_code ==0 :
        try:
            snums,results = googleResult(keywords)
        except Exception as e:
            raise(e)
        searchData(res_id,results=results)
    if len(results)>=10:
        results = results[:10]
    print(res_id)
    pUrl,pDomain,pFqdn = pathDomain(url,domain,fqdn,results)
    if pUrl:
        return 0
    elif pDomain:
        jdq = jailJudge(url,path,results,type=type)
        if jdq > 0:
            return 0
        else:
            return 1
    else:
        return 1