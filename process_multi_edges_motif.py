# -*- coding: utf-8 -*-
"""
Created on Wed Mar 31 23:11:03 2021

@author: xyj
"""
import os
import numpy as np
import scipy.sparse as sp
import itertools as it
import networkx as nx
from load_utils import *
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--start', type=int, default=0)
parser.add_argument('--end', type=int, default=724)
args = parser.parse_args()

def csr(adj,i,j):
    cols = adj.indices[adj.indptr[i]:adj.indptr[i+1]]
    if j not in cols:
        return 0
    else:
        return adj.data[adj.indptr[i] + np.argwhere(cols==j)[0][0]]

count = 0
motif_save_folder = r'E:/MasterE/Study-Exp2021/DataProcess/data-3order/motif'
edgelist_save_folder = r'E:/MasterE/Study-Exp2021/DataProcess/data-3order/edgelist'
addrs = []
for root, dirs, files in os.walk(edgelist_save_folder):
    addrs.extend(files)
    break

count = 0
for file in files:
    if count < args.start:
        count += 1
        continue
    if count >= args.end:
        break

    # Check whether the file has existed
    motif_check_path = motif_save_folder + '/' + file[:-4] + '.npy'
    if os.path.exists(motif_check_path):
        count += 1
        continue
    
    G = nx.read_weighted_edgelist(edgelist_save_folder + '/' + file, nodetype=int, create_using=nx.MultiDiGraph())
    # adj = read_adj_of(file)#.astype(dtype=np.int16).toarray()
    adj = nx.to_scipy_sparse_matrix(G)
    # get dim
    n = adj.shape[0]

    a=adj.diagonal()!=0
    adj[a,a]=0

    # adj[np.eye(n, dtype=np.bool)] = 0#remove self-loops
    # for i in range(0,n):
    #     rowsum[i,:]
    rowsum = adj.sum(axis=1)#node as the sender
    colsum = adj.sum(axis=0).T#node as the receiver
    # print(rowsum.shape, colsum[])
    motif_matrix = np.zeros((n,7), dtype=np.int32)

    # adj3 = adj.dot(adj).dot(adj)
    adj3 = adj*adj*adj
    adj3_tran1 = adj.T*adj*adj
    adj3_tran2 = adj*adj.T*adj
    adj3_tran3 = adj*adj*adj.T
    # print('finish adj3')
    for i in range(0,n):
        #type4
        motif_matrix[i][3] = csr(adj3,i,i)
        
        #type5
        # for a,b in it.combinations(adj.indices[adj.indptr[i]:adj.indptr[i+1]], 2):
        #     if a==i or b==i:
        #         continue
        #     v = (csr(adj,a,b) + csr(adj,b,a)) * csr(adj,i,b) * csr(adj,i,a)
        #     motif_matrix[i][4] += v
        #     motif_matrix[a][4] += v
        #     motif_matrix[b][4] += v
        motif_matrix[i][4] = csr(adj3_tran1,i,i) + csr(adj3_tran2,i,i) + csr(adj3_tran3,i,i)
        
        # print('finish a&b in',i)
        for j in range(0,n):
            if i==j:
                continue
            i2j = csr(adj,i,j)
            j2i = csr(adj,j,i)
            if i2j + j2i == 0:#if not connected
                continue
            # print(j)
            #type1
            motif_matrix[i][0] += (i2j * (rowsum[i,0] - i2j))/2#i to j, i to another
            motif_matrix[i][0] += j2i * (rowsum[j,0] - j2i)#j to i, j to another
            #type2
            motif_matrix[i][1] += i2j * (colsum[i,0] - j2i)#i to j, another to i
            motif_matrix[i][1] += j2i * (colsum[j,0] - i2j)#j to i, another to j
            motif_matrix[i][1] += i2j * (rowsum[j,0] - j2i)#i to j, j to another
            #type3
            motif_matrix[i][2] += (j2i * (colsum[i,0] - j2i))/2#j to i, another to i
            motif_matrix[i][2] += i2j * (colsum[j,0] - i2j)#i to j, another to j            
            
            #type6
            motif_matrix[i][5] += (i2j * (i2j - 1))/2#i to j, i to j again
            motif_matrix[i][5] += (j2i * (j2i - 1))/2#j to i, j to i again
            #type7
            motif_matrix[i][6] += i2j * j2i#i to j, j to i
        print('i/n:',i,'/',n)
    np.save(motif_check_path, motif_matrix)
    print(count)
    print(motif_matrix)
    count += 1
    # break
    
    
            


    
                
                
                
                
