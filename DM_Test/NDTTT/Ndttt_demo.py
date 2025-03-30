import pandas as pd
import json
from collections import defaultdict

# 载入数据
df = pd.read_csv('traj_sequences.csv')
df['nodes'] = df['nodes'].apply(json.loads)

# 参数设置
m_min = 2
k_min = 2

# Step 1: 生成1阶路径表
table = defaultdict(set)
for idx, row in df.iterrows():
    traj_id = row['traj_id']
    nodes = row['nodes']
    for node in set(nodes):
        table[(node,)].add(traj_id)

# Step 2: 模式增长动态遍历扩展路径
final_result = dict()

def expand_path(current_path, current_traj_ids):
    if len(current_path) >= k_min:
        final_result[current_path] = current_traj_ids

    # 尝试扩展路径
    extension_dict = defaultdict(set)
    for traj_id in current_traj_ids:
        traj_nodes = df[df['traj_id'] == traj_id]['nodes'].iloc[0]
        for idx in range(len(traj_nodes) - len(current_path)):
            if tuple(traj_nodes[idx:idx+len(current_path)]) == current_path:
                next_node = traj_nodes[idx+len(current_path)]
                extension_dict[next_node].add(traj_id)

    # 扩展并递归
    for next_node, traj_ids_set in extension_dict.items():
        if len(traj_ids_set) >= m_min:
            expand_path(current_path + (next_node,), traj_ids_set)

# 初始调用
for node, traj_ids in table.items():
    if len(traj_ids) >= m_min:
        expand_path(node, traj_ids)

# Step 3: 输出结果
result_df = pd.DataFrame({
    'hotspot_path': [list(path) for path in final_result.keys()],
    'frequency': [len(traj_ids) for traj_ids in final_result.values()],
    'traj_ids': [list(traj_ids) for traj_ids in final_result.values()]
})

result_df.to_csv('ndttt_hotspot_paths.csv', index=False)
