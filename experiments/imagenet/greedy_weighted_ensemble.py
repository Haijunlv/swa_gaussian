# 贪婪算法求解不同权重组合方案
import argparse
import os
import random
import sys
import time
import data
import glob
import copy
import pickle
import numpy as np
from scipy import optimize
from sklearn.metrics import accuracy_score
parser = argparse.ArgumentParser(description="SGD/SWA training")
parser.add_argument(
    "--pred_path",
    type=str,
    default=None,
    required=True,
    help="training directory (default: None)",
)

parser.add_argument(
    "--label_path",
    type=str,
    default=None,
    required=True,
    help="training directory (default: None)",
)


def avg_fn(averaged_model_parameter, model_parameter, num_averaged):
    return averaged_model_parameter + \
           (model_parameter - averaged_model_parameter) / (num_averaged + 1)

def greedy_ensemble(metric_np_index, pred_list, label):
    bast_acc = 0
    ensemble_logit = 0
    ensemble_list = []
    num_averaged = 0
    for i in range(len(metric_np_index)):
        avg_logit = avg_fn(ensemble_logit, pred_list[metric_np_index[i]], num_averaged)
        avg_acc = get_metric(avg_logit, label)
        print("i:{}, metric_np_index[i]:{} avg_acc:{}, bast_acc:{}， num_averaged:{}".format(i, metric_np_index[i], avg_acc, bast_acc, num_averaged))
        if avg_acc > bast_acc:
            ensemble_list.append(metric_np_index[i])
            bast_acc = avg_acc
            ensemble_logit = avg_logit
            num_averaged += 1
    print("best acc:{}, ensemble_list:{}".format(bast_acc, ensemble_list))

def get_metric(logit, label):
    y_valid_pred_cls = np.argmax(logit, axis=1)
    acc = accuracy_score(label, y_valid_pred_cls)
    return acc


def main():
    args = parser.parse_args()
    print("args:{}".format(args))
    pred_path = args.pred_path
    label_path = args.label_path

    pred_pkl_paths = glob.glob(pred_path)
    pred_list = []
    for pred_pkl_path in pred_pkl_paths:
        with open(pred_pkl_path, 'rb') as f:
            pkl = pickle.load(f, encoding='iso-8859-1')

        pred_list.append(pkl["logits"])

    with open(label_path, 'rb') as f:
        pkl = pickle.load(f, encoding='iso-8859-1')
    label = pkl["label"]

    metric_list = []
    for i, logit in enumerate(pred_list):
        acc = get_metric(logit, label)
        metric_list.append(acc)
    print("metric_list:{}".format(metric_list))

    metric_np = np.array(metric_list)
    # 降序
    metric_np_index = np.argsort(-metric_np)
    print("sort metric_list index:{}".format(metric_np_index))
    # import pdb
    # pdb.set_trace()
    greedy_ensemble(metric_np_index, pred_list, label)

if __name__ == '__main__':
    main()