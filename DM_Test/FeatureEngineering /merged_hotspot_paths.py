import pandas as pd
import ast

# === 步骤 1：加载三种算法挖掘结果 ===
ndttj = pd.read_csv("ndttj_hotspot_paths.csv")
ndttt = pd.read_csv("ndttt_hotspot_paths.csv")
tths = pd.read_csv("tths_hotspot_paths.csv")

ndttj["source_algorithm"] = "NDTTJ"
ndttt["source_algorithm"] = "NDTTT"
tths["source_algorithm"] = "TTHS"

# 将 traj_ids 从字符串转换为列表
for df in [ndttj, ndttt, tths]:
    df["hotspot_path"] = df["hotspot_path"].apply(ast.literal_eval)
    df["traj_ids"] = df["traj_ids"].apply(ast.literal_eval)

# 合并数据
all_paths = pd.concat([ndttj, ndttt, tths], ignore_index=True)

# === 步骤 2：统一路径格式字符串便于去重 ===
all_paths["path_str"] = all_paths["hotspot_path"].apply(lambda x: str(x))

# 去重（同一条路径多次挖掘的情况）
all_paths = all_paths.drop_duplicates(subset=["path_str", "frequency"])
all_paths = all_paths.reset_index(drop=True)
all_paths["path_id"] = all_paths.index

# === 步骤 3：加载 nodes 坐标信息 ===
nodes_df = pd.read_csv("nodes.csv")

# === 步骤 4：为每条热点路径中的每个节点添加坐标 ===
records = []
for _, row in all_paths.iterrows():
    path_id = row["path_id"]
    for node_id in row["hotspot_path"]:
        node_match = nodes_df[nodes_df["node_id"] == node_id]
        if not node_match.empty:
            x = node_match.iloc[0]["x"]
            y = node_match.iloc[0]["y"]
            records.append({
                "path_id": path_id,
                "node_id": node_id,
                "x": x,
                "y": y
            })

coords_df = pd.DataFrame(records)

# === 步骤 5：保存输出文件（含 traj_ids）===
all_paths[["path_id", "hotspot_path", "frequency", "source_algorithm", "traj_ids"]].to_csv("merged_hotspot_paths.csv", index=False)
coords_df.to_csv("hotspot_path_node_coords.csv", index=False)

print("已生成 merged_hotspot_paths.csv（含 traj_ids） 和 hotspot_path_node_coords.csv")
