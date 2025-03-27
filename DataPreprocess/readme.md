# 轨迹数据处理流程总结

本文档详细记录了从[原始轨迹数据](https://chorochronos.datastories.org/?q=node/10)开始，逐步进行的数据清洗、特征抽取和适配不同算法的数据预处理方案，以及对应结果输出格式。

---

## 一、原始数据文件（txt格式）

- 格式示例：
  ```csv
  traj_id,t,x,y
  1,2002-08-27 09:15:59,486253.8,4207588.1
  1,2002-08-27 09:16:29,486261.6,4207543.6
  ...
  ```

- 特点：包含轨迹ID、时间戳和空间坐标，每条轨迹包含数半之上点

---

## 二、轨迹组合 & DBSCAN 聚类

- 将同一 traj_id 的空间点按时间序进行聚合
- 使用 DBSCAN 对全部坐标点聚类，得到 Hotspot 节点
- 输出数据：
  - 聚类节点文件 `nodes.csv`
    ```csv
    node_id,x,y
    0,486253.3,4207581.0
    ...
    ```

---

## 三、 NDTTJ/NDTTT 适配格式：`traj_sequences.csv`

- 通过给定字段，将轨迹的节点序列化：
  ```csv
  traj_id,nodes,edges
  1,"[12,18,27]","[[12,18],[18,27]]"
  ...
  ```
- 适用算法：NDTTJ （路径表连接） / NDTTT （路径表遍历）
- 结果输出：`ndttj_hotspot_paths.csv`，`ndttt_hotspot_paths.csv`
  ```csv
  hotspot_path,frequency,traj_ids
  [12,18,27],4,[3,5,7,9]
  ...
  ```

---

## 四、TTHS 适配格式：Neo4j 图数据

- 节点文件：`nodes.csv`
  ```csv
  node_id,x,y
  0,486253.3,4207581.0
  ...
  ```
- 边文件：`edges.csv`
  ```csv
  source,target,frequency,traj_ids
  12,18,4,"[3,5,7,9]"
  ...
  ```
- 已通过 `py2neo` 实现自动导入 Neo4j
- 适用算法：TTHS 图网扫描和扣析算法
- 结果输出：`tths_hotspot_paths.csv`
  ```csv
  hotspot_path,frequency,traj_ids
  [5,8,11,12],3,[2,4,6]
  ...
  ```

---

## 五、各算法结果特性对比

| 算法   | 路径数 | 平均长度 | 平均频繁度 | 最适合场景 |
|--------|----------|---------------|----------------|----------------|
| NDTTJ  | 最多    | 最短          | 最高           | 热点全景统计 |
| NDTTT  | 中等    | 长             | 中             | 行为模式挖掘 |
| TTHS   | 最简约  | 长             | 最低           | 路网结构分析 |

---

