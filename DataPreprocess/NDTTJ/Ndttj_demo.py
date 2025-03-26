import pandas as pd
import json
from itertools import product

# 载入数据
df = pd.read_csv('traj_sequences.csv')
df['nodes'] = df['nodes'].apply(json.loads)

# 参数设置
m_min = 2
k_min = 2

# Step 1: 构建1阶路径表 (初始频繁节点)
table = dict()
for idx, row in df.iterrows():
    traj_id = row['traj_id']
    for node in set(row['nodes']):
        if node not in table:
            table[node] = set()
        table[node].add(traj_id)

# 频繁度过滤
freq_paths = { (node,): traj_ids for node, traj_ids in table.items() if len(traj_ids) >= m_min }

# Step 2: 逐步连接生成高阶频繁路径
k = 1
final_result = dict(freq_paths)

while k < k_min:
    candidates = dict()
    paths_list = list(freq_paths.keys())
    for path1, path2 in product(paths_list, repeat=2):
        if path1[1:] == path2[:-1]:
            new_path = path1 + (path2[-1],)
            if new_path in candidates:
                continue
            # 轨迹集合求交集计算频繁度
            traj_ids_intersection = freq_paths[path1] & freq_paths[path2]
            if len(traj_ids_intersection) >= m_min:
                candidates[new_path] = traj_ids_intersection
    if not candidates:
        break
    freq_paths = candidates
    final_result.update(freq_paths)
    k += 1

# Step 3: 结果导出
result_df = pd.DataFrame({
    'hotspot_path': [list(path) for path in final_result.keys()],
    'frequency': [len(traj_ids) for traj_ids in final_result.values()],
    'traj_ids': [list(traj_ids) for traj_ids in final_result.values()]
})

result_df.to_csv('ndttj_hotspot_paths.csv', index=False)
