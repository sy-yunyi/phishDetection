'''
Descripttion: 
version: 
Author: Six
Date: 2021-06-05 14:42:59
LastEditors: Six
LastEditTime: 2021-06-16 09:59:44
'''
import tldextract
import requests
from lxml import etree
import hashlib
import re
import os
import json
import time
import pdb

def getFQDN(domain):
    d_info = tldextract.extract(domain)
    if d_info.subdomain != "" and d_info.suffix != "":
        return d_info.subdomain, d_info.domain, d_info.suffix, d_info.subdomain+'.'+d_info.domain+'.'+d_info.suffix
    elif d_info.suffix != "":
        return d_info.subdomain, d_info.domain, d_info.suffix, d_info.domain+'.'+d_info.suffix
    elif d_info.subdomain != "":
        return d_info.subdomain, d_info.domain, d_info.suffix, d_info.subdomain+'.'+d_info.domain
    else:
        return d_info.subdomain, d_info.domain, d_info.suffix, d_info.domain

def validURL(url):
    if url.startswith("//"):
        url = "http:" + url
    elif not url.startswith("http"):
        url = "http://" + url
    
    return url


def searchData(res_id,results=None):
    
    resource_path = "data\searchData.json"
    if not os.path.exists(resource_path):
        with open(resource_path,"w") as fp:
            fp.write("/{/}")
    with open(resource_path,"r",encoding="utf-8") as fp:
        res_data = json.load(fp)
    if results:
        res_data[res_id]=results
        with open(resource_path,"w") as fp:
            json.dump(res_data,fp)
        return 3,results  # 更新数据
    else:
        if res_data.get(res_id,0)==0:
            return 0,[]  # 没有数据
        else:
            return 1,res_data.get(res_id)  # 有数据


def baiduResult(keywords):
    results = []
    headers = {
        "cookie":"PSTM=1576459250; BIDUPSID=8D3C7AA1AFC6AED754051C4F9523B6D1; __yjs_duid=1_7546734db69dd257162fdca091521f111618104292838; BDUSS=BrYi1IUkVDOEFIbTlrOWVJbktsUlRxS3lyM0NYS1hOb3VQRlZLNE5GUzFkNkJnSVFBQUFBJCQAAAAAAAAAAAEAAAD6yzUzRtWsxa7SucnxAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALXqeGC16nhgQX; BDUSS_BFESS=BrYi1IUkVDOEFIbTlrOWVJbktsUlRxS3lyM0NYS1hOb3VQRlZLNE5GUzFkNkJnSVFBQUFBJCQAAAAAAAAAAAEAAAD6yzUzRtWsxa7SucnxAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALXqeGC16nhgQX; BAIDUID=D3533264D625C1DF0EB1A39970203A87:FG=1; BAIDUID_BFESS=D3533264D625C1DF410241FA243D1782:FG=1; H_WISE_SIDS=107314_110085_127969_131423_154214_165135_165518_171235_171509_172643_173017_173617_174179_174340_174662_174682_175231_175556_175575_175678_175729_175755_175908_176123_176130_176157_176261_176341_176344_176381_176398_176551_176615_176677_176765_176869_176996_8000069_8000108_8000130_8000138_8000150_8000174; BD_UPN=12314753; delPer=1; BD_CK_SAM=1; PSINO=7; H_PS_PSSID=31660_33848_33772_33607_34077; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; COOKIE_SESSION=6040874_1_9_8_5_17_0_3_8_6_1_2_0_0_33_0_1607782699_1599141626_1613823540%7C9%231685_328_1599141623%7C9; sugstore=0; H_PS_645EC=ae111ud%2BfJa0NDrEg8BuYfb7dyS4XuTQ8h3bIrJDWxjzDyNHsRE0MYl0Wu4; BA_HECTOR=2ka00h0h0la52400kf1gbr1i70q; WWW_ST=1623033512070",
        # "PSTM=1576459250; BIDUPSID=8D3C7AA1AFC6AED754051C4F9523B6D1; H_WISE_SIDS=154599_148077_145999_154210_133333_149355_150967_152056_150077_150085_148867_155684_156087_154804_151897_153716_153444_152410_131862_154798_151533_148303_127969_154413_154175_155962_152981_155516_150346_155318_146732_154603_152572_131423_154569_154037_154782_154189_155345_154791_151872_144966_153535_154619_154117_139882_154800_154903_155237_147546_152310_154289_155865_110085; COOKIE_SESSION=4002647_1_8_8_3_11_0_2_7_5_1_2_8640908_0_33_0_1607782699_1599141626_1607782666%7C9%231685_328_1599141623%7C9; MCITY=-140%3A; BAIDUID=8496718B96BD051775300767C9051F96:FG=1; BAIDUID_BFESS=8496718B96BD051775300767C9051F96:FG=1; sugstore=0; __yjs_duid=1_89cc62687d2d89d50578db60cb2934cf1609123465304; BD_HOME=1; H_PS_PSSID=33423_1462_33418_33306_33286_33350_33313_33312_33311_33310_33414_33309_26350_33308_33307_22159_33389_33386_33370; BD_UPN=12314753; BA_HECTOR=8k21042ha4a08g2kqf1fv7kvg0q",
        "Host":"www.baidu.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36 Edg/86.0.622.51",
        "Referer": "https://www.baidu.com/"
    }
    proxies = {
    "https": "https://127.0.0.1:1080",
    "http:": "https://127.0.0.1:1080"
            }
    # proxies = getProxy()
    url = "https://www.baidu.com/s?wd={}&pn=0&rn=20&ie=UTF-8".format("%20".join(keywords))
    snums = 0
    num_flag = 0 
    try:
        res = requests.get(url,headers=headers,proxies=proxies,timeout=10)
        # pdb.set_trace()
        if len(res.text) < 10 : # 第一次可能获取不到数据
            res = requests.get(url,headers=headers,timeout=5)
        if res.status_code==200 and len(res.text) > 10:
            pdom = etree.HTML(res.text)
            # nums = pdom.xpath('//*[@id="content_left"]/div[1]/div/p[1]/b/text()')
            nums = pdom.xpath('//*[@id="container"]/div[2]/div/div[2]/span/text()')
            if len(nums)==0:
                nums = pdom.xpath('//*[@id="1"]/div/div[1]/div/p[3]/span/b/text()')
                if len(nums)==0:
                    if "没有找到" in res.text:
                        return 0,[] 
                else:
                    if "亿" in nums:
                        numbers = re.findall(r"\d+",nums[0])
                        snums = str(numbers[0] * 1000000000 + numbers[1] *10000)
                    else:
                        snums = "".join(re.findall(r"\d+",nums[0]))
            else:
                snums = "".join(re.findall(r"\d+",nums[0]))
            # print(snums)
            # /html/body/div[1]/div[3]/div[1]/div[3]/div[@class="result c-container new-pmd"]
            for ti in pdom.xpath('/html/body/div[1]/div[4]/div[1]/div[3]/div[@class="result c-container new-pmd"]'):
                try:
                    tmpi = requests.get(ti.xpath("./h3/a/@href")[0],proxies=proxies,timeout=10).url
                    results.append(tmpi)
                except Exception as e:
                    print(e)
                    # raise(e)
        else:
            time.sleep(15)
    except Exception as e:
        print(e)
        raise(e)
    if snums==0:
        snums = len(results)
    return snums,results

def googleResult(keywords):
    results = []
    headers ={
        "referer": "https://www.google.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        # "Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36 Edg/87.0.664.66",
        # "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "cookie": "CGIC=IocBdGV4dC9odG1sLGFwcGxpY2F0aW9uL3hodG1sK3htbCxhcHBsaWNhdGlvbi94bWw7cT0wLjksaW1hZ2UvYXZpZixpbWFnZS93ZWJwLGltYWdlL2FwbmcsKi8qO3E9MC44LGFwcGxpY2F0aW9uL3NpZ25lZC1leGNoYW5nZTt2PWIzO3E9MC45; CONSENT=YES+CZ.zh-CN+V14+B; HSID=AlKhsHkvVQc-G0yAd; SSID=A6oep-SbgnQOCe-Qh; APISID=cCLLK1EZUnwHtkTb/A3I7q3OUYLrAO_XmF; SAPISID=lPSaf9brvjF9cMhk/AvYG4DA-97h085Qyz; __Secure-3PAPISID=lPSaf9brvjF9cMhk/AvYG4DA-97h085Qyz; ANID=AHWqTUk2PKMnqD29EabCDntmmpRMkpk5xxC-japuLc634kFNc2BH31F-cLgoIvLa; SID=6gemR0p6g8xOvpFC055Uhkb3RcIlMvQjyiY5BFydunW09fEWnmJMZtnteZqlwmvdqqX15Q.; __Secure-3PSID=6gemR0p6g8xOvpFC055Uhkb3RcIlMvQjyiY5BFydunW09fEWVYdKEd12m5i9JzBFFrrJ6A.; OTZ=5855851_24_24__24_; SEARCH_SAMESITE=CgQIgJIB; NID=210=CA3WsRmItuAI8GvCNM7bCR2Q_SQ5CBz6HBBoH9kUoLzN0Sd6czPorLkFYNlv7AamWmJekBrQwdh-CWyvsNaGnkE4_SP4BRhWfzpu5NAmU8bq-MAmbFTPovMrniGJJTzQ8Q4NAws-eb5IALAvlDStYZAyqNcN-Mh4hoXk1hSOvQYsjdlVD-w1ieB2HSZMEfpA1V6QUZ3suWtVtzURx-IVChejyPdpa0BC1mg9OfL_2nkd1AL8e1jzAi2-1D4d8fxogmPEfspU12wCdyzIkeuKCdIfnPy81DRbvBnYCmfmxMdPH1VVHdym2D-m; 1P_JAR=2021-03-03-03; DV=0yOaKFvtlytKcKt5a0Qc82LiPpJhfxewjap4JjqDLAIAAGD139BTnYWQ1wAAAASIm0L1K13fOQAAAA; SIDCC=AJi4QfFLa-UryKz6UXjSs6WzfbuimfZf1NCr4L563fCB1UZ0fQExY3xlwh1T8OuNNQt2J3U84f4; __Secure-3PSIDCC=AJi4QfFFbq7U2SdYn-4ce4F5Z9V_ck3tgaqQ-awVC_fcFpDek2CCZLYThjWDEik7KOiyMKULOzE",
        }
    proxies = {
    "https": "http://127.0.0.1:1080",
    "http": "http://127.0.0.1:1080"
            }
    url = "https://google.com/search?source=hp&q={}&num=20&ie=UTF-8&filter=0".format("%20".join(keywords))
    # &ei=lEXgX4DBG4OxmAXq052oCQ
    print(url)
    # try:
    res = requests.get(url,headers=headers,proxies=proxies,timeout=20)
    if len(res.text) < 10 : # 第一次可能获取不到数据
        res = requests.get(url,headers=headers,timeout=5)
    if res.status_code==200:
        pdom = etree.HTML(res.text)
        # 搜索结果数量
        # if "找不到和您查询的“{}”相符的内容或信息".format("%20".join(keywords)) in res.text:
        #     return 0,[]
        # pdb.set_trace()
        snums = pdom.xpath('//*[@id="result-stats"]/text()')
        
        if len(snums)==0:
            if "抱歉没有找到" in res.text:
                return str(0),[]
        else:
            snums = "".join(re.findall(r"\d+",snums[0]))
            # //*[@id="rso"]/div/div[1]
            # //*[@id="rso"]/div/div[5]
            # //*[@id="rso"]/div/div[5]/div/div[1]/a
        # pdb.set_trace()
        for ti in pdom.xpath('//*[@id="rso"]/div/div[1]'):
            a_link = ti.xpath('./div/div[@class="yuRUbf"]/a/@href')
            if a_link ==[]:
                a_link = ti.xpath('./div/div/div[@class="yuRUbf"]/a/@href')
            if a_link ==[]:
                a_link = ti.xpath('./div[@class="yuRUbf"]/a/@href')
            if len(a_link)>0:
                results.append(a_link[0])
        if len(results)==0:
            results =pdom.xpath('//*[@class="C8nzq BmP5tf"]/@href')
    else:
        print(res.status_code)
        if res.status_code == 429:
            time.sleep(30)
        raise Exception("未获取到页面信息")  # 调用该方法时，捕获异常，若捕获到该异常，说明搜索引擎关闭了连接，需将该URL重新加入列表

    if snums == 0 or snums==[]:
        snums = len(results)
    return snums,results


def extractTitle(response,type="URL"):
    """
    提取页面标题
    输入为response对象
    输出为标题或空
    """
    if type=="URL":
        dom = etree.HTML(response.text)
    else:
        dom = etree.HTML(response)
    if dom:
        try:
            title = dom.xpath("/html/head/title/text()")
            if len(title)>0:
                return title[0].strip()
            else:
                return ""
        except:
            return ""
    else:
        return ""

def extractURL(response,type="URL"):
    if type=="URL":
        dom = etree.HTML(response.text)
    else:
        dom = etree.HTML(response)
    if dom:
        a_link = dom.xpath('//*/a/@href')
        style_link = dom.xpath('//*/link/@href')
        js_link = dom.xpath('//*/script/@src')
        image_link = dom.xpath('//*/img/@src')
        return a_link,style_link,js_link,image_link
    else:
        return [],[],[],[]

def pathDomain(url,domain,fqdn,urls):
    pUrl = 0
    pDomain = 0
    pFqdn = 0
    for ui in urls:
        _,udomain,_,ufqdn = getFQDN(ui)
        if udomain == domain:
            pDomain = 1
        if fqdn == ufqdn:
            pFqdn = 1
        if url == ui:
            pUrl = 1
        if pUrl and pDomain and pFqdn:
            return 1,1,1
    return pUrl,pDomain,pFqdn