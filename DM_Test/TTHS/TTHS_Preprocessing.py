# TTHS 数据预处理：适合Neo4j的数据生成脚本
import pandas as pd
import json
from collections import defaultdict

# Step 1: 载入已有的节点与边序列数据
df = pd.read_csv('traj_sequences.csv')
df['nodes'] = df['nodes'].apply(json.loads)
df['edges'] = df['edges'].apply(json.loads)

# Step 2: 生成节点文件（nodes.csv）
# 计算每个节点的平均坐标（推荐方式）
original_df = pd.read_csv('trucks_rev_pos.txt')

# 假设你之前使用的DBSCAN的聚类结果存在于原始数据
from sklearn.cluster import DBSCAN

# 确定聚类（需与你之前预处理时完全一致的参数）
eps, min_samples = 50, 5
db = DBSCAN(eps=eps, min_samples=min_samples)
original_df['node'] = db.fit_predict(original_df[['x','y']])
original_df = original_df[original_df['node'] != -1]

node_coords = original_df.groupby('node')[['x','y']].mean().reset_index()
node_coords.columns = ['node_id', 'x', 'y']
node_coords.to_csv('nodes.csv', index=False)

# Step 3: 生成边文件（edges.csv）
edge_freq = defaultdict(int)
edge_traj = defaultdict(set)

for _, row in df.iterrows():
    traj_id = row['traj_id']
    for edge in row['edges']:
        edge_tuple = tuple(edge)
        edge_freq[edge_tuple] += 1
        edge_traj[edge_tuple].add(traj_id)

edges_df = pd.DataFrame([{
    'source': k[0],
    'target': k[1],
    'frequency': v,
    'traj_ids': json.dumps(sorted(list(edge_traj[k])))
} for k, v in edge_freq.items()])

edges_df.to_csv('edges.csv', index=False)

print("节点和边文件已生成（nodes.csv, edges.csv）")
