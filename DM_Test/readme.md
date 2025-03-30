# 轨迹数据处理流程总结

本文档详细记录了从 [原始轨迹数据](https://chorochronos.datastories.org/?q=node/10) 开始，逐步进行的数据清洗、特征抽取和适配不同算法的数据预处理方案，以及对应结果输出格式。

---

## 一、原始数据文件（txt格式）

- 文件名：`trucks_rev_pos.txt`
- 格式示例：
  ```csv
  traj_id,t,x,y
  1,2002-08-27 09:15:59,486253.8,4207588.1
  1,2002-08-27 09:16:29,486261.6,4207543.6
  ...
  ```
- 特点：包含轨迹 ID、时间戳和空间坐标，每条轨迹包含若干点

---

## 二、轨迹组合 & DBSCAN 聚类生成节点

- 对同一 traj_id 的空间点按时间序聚合，构建轨迹序列
- 使用 DBSCAN 对所有轨迹点进行空间聚类，得到轨迹热点节点（Hotspot）
- 输出文件：`nodes.csv`
  ```csv
  node_id,x,y
  0,486253.3,4207581.0
  ...
  ```

---

## 三、轨迹节点映射与路径构建（edges文件生成）

- 根据每条轨迹中点的映射节点序列，构建轨迹在热点节点图中的表示
- 邻接节点之间构建边，统计频次、关联轨迹编号
- 输出文件：`edges.csv`
  ```csv
  source,target,frequency,traj_ids
  12,18,4,"[3,5,7,9]"
  ```

---

## 四、NDTTJ/NDTTT 适配格式（序列表）

- 输入文件：`nodes.csv` + 原始轨迹点集
- 每条轨迹被转为节点序列与边序列
- 输出文件：`traj_sequences.csv`
  ```csv
  traj_id,nodes,edges
  1,"[12,18,27]","[[12,18],[18,27]]"
  ```
- 用于执行：NDTTJ（路径表连接） 和 NDTTT（路径表遍历）
- 输出：
  - `ndttj_hotspot_paths.csv`
  - `ndttt_hotspot_paths.csv`
  ```csv
  hotspot_path,frequency,traj_ids
  [12,18,27],4,[3,5,7,9]
  ```

---

## 五、TTHS 图结构挖掘（Neo4j导入）

- 输入文件：`nodes.csv` 和 `edges.csv`
- 使用 `py2neo` 导入 Neo4j 图数据库
  - 节点类型：`Hotspot`
  - 边关系：`TRAJ_EDGE`
- 使用 TTHS 算法在图中执行路径扫描和频繁子图提取
- 输出文件：`tths_hotspot_paths.csv`
  ```csv
  hotspot_path,frequency,traj_ids
  [5,8,11,12],3,[2,4,6]
  ```

---

## 六、三种算法结果整合与统一编号

- 合并三个路径结果文件（NDTTJ、NDTTT、TTHS）
- 去重（按 path+频繁度），统一编号 path_id
- 输出文件：`merged_hotspot_paths.csv`
  ```csv
  path_id,hotspot_path,frequency,source_algorithm,traj_ids
  0,[12,18,27],4,NDTTJ,[3,5,7,9]
  ```

---

## 七、补充时间信息：起止时间字段提取

- 输入文件：`trucks_rev_pos.txt`（原始点集）
- 从每条路径对应的轨迹集合中提取最早时间、最晚时间，构建 start_time, end_time 字段
- 输出文件：`merged_hotspot_paths_with_time.csv`
  ```csv
  path_id,hotspot_path,frequency,traj_ids,start_time,end_time,source_algorithm
  0,[12,18,27],4,[3,5,7,9],09:15:59,12:34:29,NDTTJ
  ```

---

## 八、节点坐标提取并与路径关联

- 从 `merged_hotspot_paths.csv` 中提取路径节点
- 关联 `nodes.csv` 中坐标，生成路径-节点-坐标映射文件
- 输出文件：`hotspot_path_node_coords.csv`
  ```csv
  path_id,node_id,x,y
  0,12,486261.6,4207543.6
  0,18,486276.3,4206825.8
  ...
  ```

---

## 九、POI 语义增强（逆地理编码）

- 坐标系转换：EPSG:4547 → EPSG:4326（WGS84）
- 对所有节点坐标调用高德地图逆地理编码 API
- 获取最邻近 POI 的：
  - 名称（poi_name）
  - 类型编码（poi_type_code）
  - 地址（poi_address）
  - 类型（poi_type） ← 根据编码匹配中类中文名称
- 输入：`nodes.csv`（全部节点）
- 输出：`nodes_with_poi.csv`
  ```csv
  node_id,x,y,lon,lat,poi_name,poi_type_code,poi_type,poi_address
  0,486253.3,4207581.0,113.84,38.01,红岩岭景区,110000,风景名胜相关,岔口乡主铺掌村北沟
  ```

---

## 十、当前阶段成果文件列表（部分）

- `trucks_rev_pos.txt`：原始点集
- `nodes.csv`：热点节点
- `edges.csv`：热点边结构
- `traj_sequences.csv`：NDTTJ/NDTTT输入
- `ndttj_hotspot_paths.csv` / `ndttt_hotspot_paths.csv` / `tths_hotspot_paths.csv`：三类挖掘结果
- `merged_hotspot_paths.csv`：整合并编号
- `merged_hotspot_paths_with_time.csv`：整合并添加时间
- `hotspot_path_node_coords.csv`：路径-节点-坐标映射
- `nodes_with_poi.csv`：节点POI增强结果

---

