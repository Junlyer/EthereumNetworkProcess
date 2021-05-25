# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 20:14:07 2021

@author: xyj
"""
#首先将交易文件构建为图G，有向多边图
#然后，找到中心节点的二阶领域
#生成二阶邻域内节点的index，并存储成txt文件
#提取二阶邻域内节点的特征，存储成txt文件
#生成二阶邻域内节点之间连边的edgelist，权值为多重边边数，存储成txt文件

def error_log(addr):
    f = open(r'E:\MasterE\Study-Exp2021\DataProcess\data-3order\error_log.txt', 'a')
    f.write(addr+'\n')
    f.close()
    return

import os
import numpy as np
import scipy.sparse as sp
import matplotlib.pyplot as plt
import networkx as nx
from load_utils import *

files = get_file_list()
count = 0

for file in files:
    file = file.lower()
    addr = file.replace('.csv', '')
    index_check_path = r'E:\MasterE\Study-Exp2021\DataProcess\data-3order\index' + '\\' + file.replace('.csv', '') + '.txt'
    feature_check_path = r'E:\MasterE\Study-Exp2021\DataProcess\data-3order\feature' + '\\' + file.replace('.csv', '') + '.txt'
    edgelist_check_path = r'E:\MasterE\Study-Exp2021\DataProcess\data-3order\edgelist' + '\\' + file.replace('.csv', '') + '.txt'
    
    if os.path.exists(index_check_path) and os.path.exists(feature_check_path) and os.path.exists(edgelist_check_path):
        count += 1
        continue
    
    #写or读节点index文件
    if not os.path.exists(index_check_path):
        neighbor_2hop = find_2hop_neighbor(file)
        if len(neighbor_2hop) == 0:
            error_log(file)
            continue
        nodes_2hop = [addr] + neighbor_2hop
        num_2hop = len(nodes_2hop)
        node_idx = dict()
        for idx in range(num_2hop):
            node_idx[nodes_2hop[idx]] = idx
        with open(index_check_path, 'w') as f:
            for k, v in node_idx.items():
                f.write(str(k) + ' ' + str(v) + '\n')
            f.close()
    else:
        f = open(index_check_path, 'r')
        node_idx = dict()
        nodes_2hop = []
        for line in f:
            info = line.split(' ')
            node_idx[info[0]] = info[1]
            nodes_2hop.append(info[0])
        f.close()
    print('-----finish index')
    
    G = get_multidigraph_of(file)
    
    #写节点feature文件
    if not os.path.exists(feature_check_path):
        features = get_features_of(G, nodes_2hop)
        with open(feature_check_path, 'w') as f:
            for idx in range(len(features)):
                f.write(str(idx))
                for item in features[idx]:
                    f.write(' ' + str(item))
                f.write('\n')
            f.close()
    
    print('-----finish feature')
    
    #写节点edgelist文件
    if not os.path.exists(edgelist_check_path):
        with open(edgelist_check_path, 'w') as f:
            H = nx.DiGraph(G.subgraph(nodes_2hop))
            for line in nx.generate_edgelist(H, data=False):
                nodes = line.split(' ')
                idx1 = node_idx[nodes[0]]
                idx2 = node_idx[nodes[1]]
                weight = G.number_of_edges(nodes[0], nodes[1])
                f.write(str(idx1) + ' ' + str(idx2) + ' ' + str(weight) + '\n')
            f.close()
    
    print('-----finish edgelist')
    
    print(count, file, 'finish')
    count += 1