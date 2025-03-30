from neo4j import GraphDatabase
import pandas as pd
import json

# Neo4j数据库连接参数（你需修改为自己的实际参数）
uri = "bolt://localhost:7687"
user = "neo4j"
password = "#020728Ceq"

# 连接 Neo4j 驱动
driver = GraphDatabase.driver(uri, auth=(user, password))

# 导入节点数据函数
def import_nodes(tx, node_id, x, y):
    tx.run("""
        MERGE (n:Hotspot {id: $node_id})
        SET n.x = $x, n.y = $y
    """, node_id=node_id, x=x, y=y)

# 导入边数据函数
def import_edges(tx, source, target, frequency, traj_ids):
    tx.run("""
        MATCH (src:Hotspot {id: $source})
        MATCH (tgt:Hotspot {id: $target})
        MERGE (src)-[r:TRAJ_EDGE]->(tgt)
        SET r.frequency = $frequency, r.traj_ids = $traj_ids
    """, source=source, target=target, frequency=frequency, traj_ids=traj_ids)

# 执行数据导入
with driver.session() as session:
    # 导入节点
    nodes_df = pd.read_csv('nodes.csv')
    for _, row in nodes_df.iterrows():
        session.execute_write(import_nodes, int(row['node_id']), float(row['x']), float(row['y']))

    # 导入边
    edges_df = pd.read_csv('edges.csv')
    for _, row in edges_df.iterrows():
        session.execute_write(
            import_edges,
            int(row['source']),
            int(row['target']),
            int(row['frequency']),
            row['traj_ids']
        )

print("节点和边数据导入Neo4j完成！")

# 关闭连接
driver.close()