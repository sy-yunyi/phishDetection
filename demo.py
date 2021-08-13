from jail import jailPhish
from pandas.core import base
from ldpImp import LDP
import os
import pandas as pd
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




if __name__=="__main__":
    data = pediaData(type="normal")
    for di in data:
        try:
            # print(LDP(di[0],di[1],type="file"))
            print(jailPhish(di[0],di[1],type="file"))
        except Exception as e:
            if e.__str__()=="未获取到页面信息":
                pass  # 搜索引擎屏蔽

