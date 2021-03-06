# -*- coding: utf-8 -*-
"""
Created on Thu Mar 25 15:14:41 2021

@author: xyj
"""

import os
import scipy.sparse as sp
import pandas as pd
import numpy as np
import networkx as nx
# import matplotlib.pyplot as plt

ROOT = r'E:\MasterE\Study-Exp2021\etherscan-spider' 
folder = ROOT + r'\data-3order\data_dropduplicate'


def get_file_list():
    for root, dir, files in os.walk(folder):
        return files

def get_trans_of(filepath):
    # complete_path = folder + '\\' + filename
    complete_path = filepath
    trans = pd.read_csv(complete_path, header=0, index_col=None)
    if 'isError' in trans.columns:
        trans = trans[trans['isError'] != 1]
    trans = trans.dropna(subset=['from','to']) # 'to' will be NaN if the transaction is generated by creating contracts
    return trans

def get_multidigraph_of(filepath):
    trans = get_trans_of(filepath)
    G = nx.from_pandas_edgelist(trans, 'from', 'to', edge_attr=['value','timeStamp'], edge_key='hash', create_using=nx.MultiDiGraph())
    return G

def get_graph_of(filepath, gtype=nx.MultiDiGraph()):
    trans = get_trans_of(filepath)
    G = nx.from_pandas_edgelist(trans, 'from', 'to', edge_attr=['value','timeStamp'], edge_key='hash', create_using=gtype)
    return G

#找到二阶邻域
def find_2hop_neighbor(filepath):
    G = get_graph_of(filepath, gtype=nx.Graph())
    filepath = filepath
    if '/' in filepath.replace('\\', '/'):
        filename = filepath.split('/')[-1]
    cnode = filename.replace('.csv', '')
    if not cnode in list(G.nodes):
        return []
    hop_dict = dict(nx.bfs_successors(G, source=cnode, depth_limit=2))
    nodes_2hop = []
    for k, v in hop_dict.items():
        nodes_2hop = nodes_2hop + v
    return nodes_2hop

# def read_2hop_neighbor(filename):
#     f = open(index_check_path, 'r')
#     nodes_2hop = []
#     for line in f:
#         info = line.split(' ')
#         nodes_2hop.append(info[0])
#     return nodes_2hop


def get_node_index_dict(Gnodes):
    # 将每个节点映射到index
    # nodes为G.nodes格式
    node_idx = {}
    index = 0
    for node in Gnodes:
        node_idx[node] = index
        index += 1
    return node_idx

def get_adj_of(G):
    # G = get_multidigraph_of(filename)
    node_idx = get_node_index_dict(G.nodes)
    # Task1:提取邻接矩阵
    # 迭代G.adj，创建邻接矩阵，Aij代表从节点i出发到达节点j的有向边的数量
    source, target, value = [], [], [] # 出边的source & target & value
    for n, nbrsdict in G.adjacency():
        for nbr, keydict in nbrsdict.items():
            s = node_idx[n]
            t = node_idx[nbr]
            v = len(keydict)
            source.append(s)
            target.append(t)
            value.append(v)
    # 确保稀疏邻接矩阵行列是(n, n)
    source.append(len(G.nodes)-1)
    target.append(len(G.nodes)-1)
    value.append(0)
    #构建稀疏矩阵
    adj_sp = sp.csr_matrix((value, (source, target)))
    return adj_sp

def get_features_of(G, target_nodes):
    # G = get_multidigraph_of(filename)
    # node_idx = get_node_index_dict(G.nodes)
    # Task2:提取特征矩阵 13个特征
    # amount, in_amount, out_amount: 
    # degree, in_degree, out_degree: G.degree(), G.in_degree(), G.out_degree()
    # neighbor, in_neighbor, out_neighbor: sum of G.neighbors() + G.reverse().neighbors()
    # freq, in_freq, out_freq: timespan=max_timestamp-min_timestamp (=0?) /timespan
    # balance
    rG = G.reverse()
    all_features = []
    # print(target_nodes)
    for i in range(len(target_nodes)):
        node = list(target_nodes)[i]
        all_values = []
        max_timestamp = 0
        min_timestamp = 5000000000
        # 所有出边的
        for nbr, datadict in G.adj[node].items():
            for key, values in datadict.items():
                eattr = list(dict(values).values())
                out_value = int(eattr[0])
                timestamp = eattr[1]
                if timestamp > max_timestamp:
                    max_timestamp = timestamp
                if timestamp < min_timestamp:
                    min_timestamp = timestamp
                all_values.append(out_value)
        # 所有入边的
        for nbr, datadict in rG.adj[node].items():
            for key, values in datadict.items():
                eattr = list(dict(values).values())
                in_value = int(eattr[0])
                timestamp = eattr[1]
                if timestamp > max_timestamp:
                    max_timestamp = timestamp
                if timestamp < min_timestamp:
                    min_timestamp = timestamp
                all_values.append(in_value)
        all_values = [v/1000000000000000000 for v in all_values]
        # calculate features
        # 3:amount
        out_amount = sum(all_values[:G.out_degree(node)])
        in_amount = sum(all_values[G.out_degree(node):])
        total_amount = out_amount + in_amount
        # 3:degree
        out_degree = G.out_degree(node)
        in_degree = G.in_degree(node)
        total_degree = out_degree + in_degree
        # 3:neighbor
        out_neighbor = len(list(G.neighbors(node)))
        in_neighbor = len(list(rG.neighbors(node)))
        total_neighbor = out_neighbor + in_neighbor
        # 3:freq
        timespan = max_timestamp - min_timestamp
        if timespan != 0:
            out_freq = out_degree / timespan
            in_freq = in_degree / timespan
            total_freq = total_degree / timespan
        else:
            out_freq = in_freq = total_freq = 0
        # 1:balance
        balance = in_amount - out_amount
        # gather all features
        features = [out_amount, in_amount, total_amount,
                    out_degree, in_degree, total_degree,
                    out_neighbor, in_neighbor, total_neighbor,
                    out_freq, in_freq, total_freq,
                    balance]
        all_features.append(features)
    # all_features = np.array(all_features)
    return all_features

def get_processed_data_of(filename):
    G = get_multidigraph_of(filename)
    adj_sp = get_adj_of(G)
    all_features = get_features_of(G)
    return adj_sp, all_features
    
def read_adj_of(filename):
    # ROOT = r'E:\MasterE\Study-Exp2021\DataProcess'
    adj_folder = r'.\Adj'
    filename = filename.replace('100_', '')
    adj_sp = sp.load_npz(adj_folder + '\\' + filename)
    return adj_sp


