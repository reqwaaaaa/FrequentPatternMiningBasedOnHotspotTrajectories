import pandas as pd
from sklearn.cluster import DBSCAN
import json

# DBSCAN算法参数（空间聚类，用于确定热点节点）
EPS = 50            # 空间聚类半径（米），推荐30-100米
MIN_SAMPLES = 5     # 最少轨迹点数以形成一个热点节点，论文中常取5

# 数据输入与输出文件名
INPUT_FILE = 'trucks_rev_pos.txt'
OUTPUT_FILE = 'traj_sequences.csv'

# ==================== Step 1 数据加载与清洗 ====================

df = pd.read_csv(INPUT_FILE)

# 删除坐标完全重复的数据点
df = df.drop_duplicates(subset=['traj_id', 'x', 'y'])

# 数据按轨迹ID和时间排序
df = df.sort_values(by=['traj_id', 't']).reset_index(drop=True)

# ==================== Step 2 热点节点聚类生成 ====================

# 使用DBSCAN生成热点节点，论文推荐DBSCAN
db = DBSCAN(eps=EPS, min_samples=MIN_SAMPLES)
df['node'] = db.fit_predict(df[['x', 'y']])

# 移除DBSCAN中的噪声节点（标记为-1）
df = df[df['node'] != -1].reset_index(drop=True)

# ==================== Step 3 形成节点序列与边序列 ====================

trajectory_sequences = []
for traj_id, group in df.groupby('traj_id'):
    nodes = group['node'].tolist()

    # 去除轨迹序列中连续重复的节点（只保留首次进入节点）
    nodes_clean = [nodes[0]]
    for n in nodes[1:]:
        if n != nodes_clean[-1]:
            nodes_clean.append(n)

    # 论文明确要求：至少2个节点构成路径，长度不足则忽略
    if len(nodes_clean) < 2:
        continue

    # 根据节点序列构造边序列
    edges = [(nodes_clean[i], nodes_clean[i + 1]) for i in range(len(nodes_clean) - 1)]

    trajectory_sequences.append({
        'traj_id': traj_id,
        'nodes': nodes_clean,
        'edges': edges
    })

# ==================== Step 4 输出CSV文件 ====================

# 为确保文件格式清晰，节点序列与边序列使用json格式导出
output_df = pd.DataFrame({
    'traj_id': [t['traj_id'] for t in trajectory_sequences],
    'nodes': [json.dumps(t['nodes']) for t in trajectory_sequences],
    'edges': [json.dumps(t['edges']) for t in trajectory_sequences]
})

# 输出CSV文件，符合NDTTJ/NDTTT算法输入要求
output_df.to_csv(OUTPUT_FILE, index=False)

print(f"数据预处理完成，结果保存至文件：{OUTPUT_FILE}")
