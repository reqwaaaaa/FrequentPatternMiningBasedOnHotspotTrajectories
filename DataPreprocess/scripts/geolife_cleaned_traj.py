import os
import pandas as pd
from glob import glob
from tqdm import tqdm
from datetime import datetime, timedelta

base_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(base_dir, '..'))
data_dir = os.path.join(root_dir, 'Geolife Trajectories 1.3', 'Data')
output_path = os.path.join(root_dir, 'outputs')
os.makedirs(output_path, exist_ok=True)

# 统计每个用户的轨迹数量
user_dirs = sorted([d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))])
user_traj_counts = []

for user in user_dirs:
    traj_dir = os.path.join(data_dir, user, 'Trajectory')
    if os.path.exists(traj_dir):
        plt_files = glob(os.path.join(traj_dir, '*.plt'))
        user_traj_counts.append((user, len(plt_files)))

# 选取轨迹数量适中的用户（70~120）
selected_users = [user for user, cnt in user_traj_counts if 70 <= cnt <= 120]

all_records = []

for user in tqdm(selected_users, desc="处理用户"):
    traj_dir = os.path.join(data_dir, user, 'Trajectory')
    plt_files = sorted(glob(os.path.join(traj_dir, '*.plt')))

    for traj_id, file_path in enumerate(plt_files, start=1):
        with open(file_path, 'r') as f:
            lines = f.readlines()[6:]  # 跳过前6行 header

        last_time = None
        for line in lines:
            parts = line.strip().split(',')
            if len(parts) >= 7:
                lat = float(parts[0])
                lon = float(parts[1])
                date = parts[5]
                time = parts[6]
                timestamp = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")

                # 每隔一刻钟取一个点
                if last_time is None or (timestamp - last_time) >= timedelta(minutes=15):
                    all_records.append([user, traj_id, timestamp.strftime('%Y-%m-%d %H:%M:%S'), lon, lat])
                    last_time = timestamp

columns = ['uid', 'traj_id', 't', 'x', 'y']
df = pd.DataFrame(all_records, columns=columns)
df.to_csv(os.path.join(output_path, 'geolife_cleaned_traj.csv'), index=False)

print("清洗完成，输出文件已保存：outputs/geolife_cleaned_traj.csv")
