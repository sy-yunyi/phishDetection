'''
Descripttion: 
version: 
Author: Six
Date: 2021-06-15 14:13:06
LastEditors: Six
LastEditTime: 2021-06-15 15:40:55
'''
"""
对数据扩增结果进行处理
1. 去除无效URL
2. 过滤相同域名和路径的URL
"""

import json
from hhpImp import spGenerate

def validUniqueURL(file_path,out_path,domain_dis):
    with open(file_path,"r",encoding="utf-8") as fp:
        lines = fp.readlines()
        lines = [line.strip() for line in lines if (line.strip().startswith("https://") or line.strip().startswith("http://") or line.strip().startswith("//")) and "." in line]
    res_list = []
    tmp_dict = {}
    # lines = ["https://osact.gtarcade.com/platform/apps/download/index.html","https://sssea.gtarcade.com/"]
    for line in lines:
        print(line)
        if line.startswith("//"):
            line = "http:"+line
        fqdn, upath = spGenerate(line)
        index = fqdn+"-"+upath
        if index not in tmp_dict.keys():
            tmp_dict[index] = 1
            res_list.append(line)
        else:
            tmp_dict[index] = tmp_dict[index] + 1
    with open(out_path,"w",encoding="utf-8") as fp:
        for li in res_list:
            fp.write(li+"\n")
    with open(domain_dis,"w") as fp:
        json.dump(tmp_dict,fp)

if __name__ == "__main__":
    file_path = r"F:\phishDetection\data\searchExtendURL.txt"
    out_path = r"F:\phishDetection\raw_data\searchExtendURL.txt"
    domain_dis = r"F:\phishDetection\data\searchExtendDomain.json"
    validUniqueURL(file_path,out_path,domain_dis)

