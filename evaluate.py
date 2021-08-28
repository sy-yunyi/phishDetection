from sklearn.metrics import accuracy_score,recall_score,classification_report,f1_score,precision_score
from sklearn import metrics
import pdb
import pandas as pd

def eval_func(y_test,predictions_binarized):
    print('Accuracy: %s' % accuracy_score(y_test, predictions_binarized))
    print('F1 score: %s' % f1_score(y_test, predictions_binarized))
    print('Precision_score: %s' % precision_score(y_test, predictions_binarized))
    print('Recall_score: %s' % recall_score(y_test, predictions_binarized))
    print(metrics.confusion_matrix(y_test,predictions_binarized))
    print(classification_report(y_test, predictions_binarized))


def eval_search():
    data_path = r"data\hhp_normal.txt"
    fp = open(data_path,"r")
    lines = fp.readlines()
    lines = [line.strip().split("\t")[2] for line in lines]
    y_test = [0] * len(lines)
    predictions_binarized = list(map(int,lines))
    predictions_binarized = [0 if i==0 else 1 for i in predictions_binarized]

    data_path = r"data\hhp_phish.txt"
    fp = open(data_path,"r")
    lines = fp.readlines()
    lines = [line.strip().split("\t")[2] for line in lines]
    y_test = y_test + [1] * len(lines)

    predictions_binarized = predictions_binarized + [0 if i==0 else 1 for i in list(map(int,lines))]
    eval_func(y_test,predictions_binarized)
# pdb.set_trace()
def eval_pedia():
    normal_path = r"data\eval_data\normal_pedia_pedia.txt"
    phish_path = r"data\eval_data\phish_pedia_pedia.txt"
    normal_df = pd.read_csv(normal_path,delimiter="\t")
    phish_df = pd.read_csv(phish_path,delimiter="\t")
    pre1 = normal_df["phish"]
    pre2 = phish_df["phish"]
    y_test = [0] * len(list(map(int,pre1.values))) + [1] * len(list(map(int,pre2.values)))
    predictions_binarized = list(map(int,pre1.values)) + list(map(int,pre2.values))
    eval_func(y_test,predictions_binarized)
eval_search()