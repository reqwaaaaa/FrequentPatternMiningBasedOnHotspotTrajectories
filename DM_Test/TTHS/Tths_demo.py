import sys
import json
import pandas as pd
from py2neo import Graph

# 提高递归深度上限，避免深路径超限错误
sys.setrecursionlimit(3000)

# === 参数设置 ===
k_min = 2  # 最小路径长度（节点数）
m_min = 2  # 最小频繁度（覆盖轨迹数）

# === 连接 Neo4j 图数据库 ===
graph = Graph("bolt://localhost:7687", auth=("neo4j", "#020728Ceq"))

# === 用于存储热点路径结果 ===
hotspot_results = []
visited_paths = set()  # 避免重复路径

# === 剪枝递归优化函数 ===
def dfs(current_node_id, current_path, current_traj_set):
    current_path.append(current_node_id)

    query = """
    MATCH (n:Hotspot {id: $node_id})-[r:TRAJ_EDGE]->(m:Hotspot)
    WHERE r.frequency >= $m_min
    RETURN m.id AS next_id, r.traj_ids AS traj_ids
    """
    result = graph.run(query, node_id=current_node_id, m_min=m_min).data()

    leaf = True
    for record in result:
        next_id = record['next_id']
        if next_id in current_path:
            continue  # 防止回环造成死递归

        try:
            next_trajs = set(json.loads(record['traj_ids']))
        except Exception:
            continue

        intersection = current_traj_set & next_trajs

        if len(intersection) >= m_min:
            leaf = False
            dfs(next_id, current_path.copy(), intersection)

    if leaf and len(current_path) >= k_min:
        path_tuple = tuple(current_path)
        if path_tuple not in visited_paths:
            visited_paths.add(path_tuple)
            hotspot_results.append({
                'hotspot_path': current_path,
                'frequency': len(current_traj_set),
                'traj_ids': sorted(list(current_traj_set))
            })

# === 主函数遍历所有起点节点 ===
def run_tths():
    nodes = graph.run("MATCH (n:Hotspot) RETURN n.id AS id").data()
    for record in nodes:
        node_id = record['id']

        q = """
        MATCH (n:Hotspot {id: $node_id})-[r:TRAJ_EDGE]->()
        WHERE r.frequency >= $m_min
        RETURN collect(DISTINCT r.traj_ids) AS traj_lists
        """
        traj_result = graph.run(q, node_id=node_id, m_min=m_min).evaluate()

        if traj_result:
            try:
                traj_sets = [set(json.loads(t)) for t in traj_result]
                initial_traj_set = set.union(*traj_sets)
                dfs(node_id, [], initial_traj_set)
            except Exception as e:
                print(f"轨迹解析失败 @ node {node_id}：", e)

    # === 保存为CSV ===
    df = pd.DataFrame(hotspot_results)
    df.to_csv("tths_hotspot_paths.csv", index=False)
    print("TTHS热点轨迹挖掘完成，结果保存为 tths_hotspot_paths.csv")

# === 执行 ===
if __name__ == "__main__":
    run_tths()
