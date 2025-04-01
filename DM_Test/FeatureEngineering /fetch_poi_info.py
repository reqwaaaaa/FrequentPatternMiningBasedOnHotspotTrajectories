import pandas as pd
import requests
import time
import os
from tqdm import tqdm
from pyproj import Transformer

# === 配置 ===
API_KEY = "your api key"
INPUT_CSV = "nodes.csv"
OUTPUT_CSV = "nodes_with_poi.csv"
CACHE_FILE = "poi_cache_nodes.csv"

# EPSG:4547 → EPSG:4326
transformer = Transformer.from_crs("EPSG:4547", "EPSG:4326", always_xy=True)

# === 读取原始节点 ===
df = pd.read_csv(INPUT_CSV)
df["wgs84_coord"] = df.apply(lambda row: transformer.transform(row["x"], row["y"]), axis=1)
df[["lon", "lat"]] = pd.DataFrame(df["wgs84_coord"].tolist(), index=df.index)
df["wgs84_coord_str"] = df[["lon", "lat"]].astype(str).agg(",".join, axis=1)

# === 加载缓存 ===
if os.path.exists(CACHE_FILE):
    cache_df = pd.read_csv(CACHE_FILE)
else:
    cache_df = pd.DataFrame(columns=["wgs84_coord_str", "poi_name", "poi_type", "poi_address"])

poi_cache = dict(zip(cache_df["wgs84_coord_str"], cache_df[["poi_name", "poi_type", "poi_address"]].values))

# === 查询 POI ===
results = []
for _, row in tqdm(df.iterrows(), total=len(df), desc="查询 POI"):
    coord = row["wgs84_coord_str"]
    if coord in poi_cache:
        name, type_, addr = poi_cache[coord]
    else:
        try:
            url = "https://restapi.amap.com/v3/geocode/regeo"
            params = {
                "key": API_KEY,
                "location": coord,
                "radius": 300,
                "extensions": "all"
            }
            resp = requests.get(url, params=params, timeout=5)
            data = resp.json()
            pois = data.get("regeocode", {}).get("pois", [])
            if pois:
                top = pois[0]
                name = top.get("name", "")
                type_ = top.get("type", "")
                addr = top.get("address", "")
            else:
                name = type_ = addr = ""
            poi_cache[coord] = [name, type_, addr]
            time.sleep(0.15)  # 限速保护
        except Exception as e:
            print(f"[错误] {coord} 查询失败：{e}")
            name = type_ = addr = ""
    
    results.append({
        "node_id": row["node_id"],
        "x": row["x"],
        "y": row["y"],
        "lon": row["lon"],
        "lat": row["lat"],
        "poi_name": name,
        "poi_type": type_,
        "poi_address": addr
    })

# === 保存结果 ===
poi_df = pd.DataFrame(results)
poi_df.to_csv(OUTPUT_CSV, index=False)

# 更新缓存
pd.DataFrame([
    {"wgs84_coord_str": k, "poi_name": v[0], "poi_type": v[1], "poi_address": v[2]}
    for k, v in poi_cache.items()
]).to_csv(CACHE_FILE, index=False)

print("所有节点POI增强完成,输出保存至:", OUTPUT_CSV)
