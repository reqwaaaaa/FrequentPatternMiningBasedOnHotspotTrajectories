import pandas as pd
import ast
from statistics import median

# === Step 1: 加载原始点数据 trucks_rev_pos.txt ===
raw_df = pd.read_csv("trucks_rev_pos.txt")
raw_df["t"] = pd.to_datetime(raw_df["t"])

# 提取每个 traj_id 的起始时间、终止时间
traj_times = raw_df.groupby("traj_id")["t"].agg(["min", "max"])
traj_times["start_time"] = traj_times["min"].dt.time
traj_times["end_time"] = traj_times["max"].dt.time
traj_times = traj_times[["start_time", "end_time"]]

# === Step 2: 加载热点路径文件 ===
merged_df = pd.read_csv("merged_hotspot_paths.csv")

# 将字符串形式的 list 转为真正的 list
merged_df["traj_ids"] = merged_df["traj_ids"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

# === Step 3: 对每行计算时间特征 ===
def get_median_time(traj_ids, time_type):
    times = []
    for tid in traj_ids:
        if tid in traj_times.index:
            t = traj_times.loc[tid, time_type]
            times.append(pd.to_datetime(t.strftime("%H:%M:%S")))
    if not times:
        return None
    return pd.Series(times).median().time()

# 计算中位起始时间和终止时间
merged_df["median_start_time"] = merged_df["traj_ids"].apply(lambda tids: get_median_time(tids, "start_time"))
merged_df["median_end_time"] = merged_df["traj_ids"].apply(lambda tids: get_median_time(tids, "end_time"))

# === Step 4: 输出结果 ===
output_cols = ["path_id", "hotspot_path", "frequency", "source_algorithm", "traj_ids", "median_start_time", "median_end_time"]
merged_df[output_cols].to_csv("merged_hotspot_paths_with_time.csv", index=False)

print("已生成 merged_hotspot_paths_with_time.csv，新增时间特征。")
