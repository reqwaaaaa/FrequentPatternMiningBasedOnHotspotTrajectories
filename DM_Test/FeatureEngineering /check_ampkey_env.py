import requests

# === 高德 API Key（web服务，不是web端!）===
API_KEY = "your apikey"

# === 测试坐标（WGS84 经纬度格式）===
test_coord = "23.845098,38.018473"

# === 调用逆地理编码 API ===
url = "https://restapi.amap.com/v3/geocode/regeo"
params = {
    "key": API_KEY,
    "location": test_coord,
    "radius": 300,          # 查询半径（米）
    "extensions": "all",    # 返回详细信息（包含 POI）
}

print(f"正在查询坐标：{test_coord}")
resp = requests.get(url, params=params, timeout=10)
data = resp.json()

# === 输出原始返回结果 ===
print("\n=== 原始返回 JSON ===")
print(data)

# === 提取并打印 POI 信息 ===
print("\n=== POI 列表信息（前3个）===")
pois = data.get("regeocode", {}).get("pois", [])
if pois:
    for poi in pois[:3]:
        print(f"- 名称: {poi.get('name')}")
        print(f"  类型编码: {poi.get('type')}")
        print(f"  地址: {poi.get('address')}")
        print(f"  分类: {poi.get('typecode')}")
        print()
else:
    print("未返回 POI（可能是郊区/无兴趣点）")
