from jail import jailPhish
from pandas.core import base
from ldpImp import LDP
import os
import time
import pandas as pd
from tqdm import tqdm
from queue import Queue
import threading
import base64




def pediaData(type="phish"):
    phish_path = r"data\phish_clean.csv"
    normal_path = r"data\normal_clean.csv"
    data = []
    phish_dict = {}
    if type=="phish":
        df = pd.read_csv(phish_path)
        pids = []
        for di in df.iloc:
            phish_dict[di['id']] = di['URL']
        for root, dir, files in os.walk(r"F:\phish_v2\data_html\pedia\phish"):
            for file in files:
                pid = int(file.split("_")[-1].split(".")[0])
                pids.append(pid)
                if phish_dict.get(pid,0)!=0:
                    data.append([phish_dict[pid],os.path.join(root,file)])
                # else:
                #     print(pid)
    else:
        df = pd.read_csv(normal_path)
        for di in df.iloc:
            data.append([di["URL"]])
        for root, dir, files in os.walk(r"F:\phish_v2\data_html\pedia\normal"):
            for file in files:
                ub64 = file.split("_")[-1].split(".")[0]
                cur_u = base64.b64decode(ub64).decode()
                if [cur_u] in data:
                    data[data.index([cur_u])].extend([os.path.join(root,file)])

    return data



def getTest():
    file_path = r"G:\bak\hp-f\phishDetection\data\normal_final.csv"
    df = pd.read_csv(file_path)
    return df['dir'].values,df['url'].values


# r"F:\研究方案\钓鱼检测框架-PhishTotal\Phishpedia\phish_sample_30k"
# def pediaData_v2(type="phish"):
#     dirs,urls = getTest()

def detect_exec(data_queue):
    data_path = r"F:\研究方案\钓鱼检测框架-PhishTotal\Phishpedia\benign_sample_30k"
    while(not data_queue.empty()):
        item = data_queue.get()
        url,dir = item[1],item[0]
        if url in open(r"G:\bak\hp-f\phishDetection\jail_normal.txt","r",encoding="ISO-8859-1").read():
            print("have done")
            continue
        fp_pre = open("jail_normal.txt","a+")
        try:
            dir.replace("<token>",",")
            url.replace("<token>",",")
            print(url)
            # print(LDP(ui,os.path.join(os.path.join(data_path,di),"html.txt"),type="file"))
            res = jailPhish(url,os.path.join(os.path.join(data_path,dir),"html.txt"),type="file")
            print(res)
            fp_pre.write(url+"\t"+dir+"\t"+str(res)+"\t"+"detection"+"\n")
        except Exception as e:
            if e.__str__()=="未获取到页面信息":
                time.sleep(5)
                # 搜索引擎屏蔽
            print(e)
            fp_pre.write(url+"\t"+dir+"\t"+str(3)+"\t"+str(e)+"\n")
        fp_pre.close()


def dataClean():
    file_path =r"data/hhp_normal.txt"
    with open(file_path,"r",encoding="utf-8") as fp:
        lines = fp.readlines()
        lines = [line.strip().split("\t") for line in lines]
        lines = [line for line in lines if line[3]!="-1"]
        lines = [line for line in lines if line[2]!="3"]
        lines = [line for line in lines if line[2]!="1"]
    with open(file_path,"w",encoding="utf-8") as fp:
        for line in lines:
            fp.write("\t".join(line)+"\n")



if __name__=="__main__":
    # data = pediaData_v2(type="normal")
    
    dataClean()


    # dirs,urls = getTest()
    # dataq = Queue()
    
    # for di,ui in tqdm(zip(dirs,urls)):
    #     dataq.put([di,ui])

    # t_list = []
    # for i in range(12):
    #     t = threading.Thread(target=detect_exec, args=(dataq,))
    #     t.start()
    #     t_list.append(t)
    
    # for ti in t_list:
    #     ti.join()
    
    
    
    

