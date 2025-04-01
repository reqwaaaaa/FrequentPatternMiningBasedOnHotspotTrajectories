from neo4j import GraphDatabase

# 请自行修改为你自己的密码
uri = "bolt://localhost:7687"
user = "neo4j"
password = "your neo4j password"

driver = GraphDatabase.driver(uri, auth=(user, password))

def check_data(tx):
    print("节点数量：")
    for record in tx.run("MATCH (n) RETURN count(n) AS count"):
        print(record["count"])
    
    print("关系数量：")
    for record in tx.run("MATCH ()-[r]->() RETURN count(r) AS count"):
        print(record["count"])

    print("所有节点标签：")
    for record in tx.run("CALL db.labels()"):
        print(record["label"])

    print("所有关系类型：")
    for record in tx.run("CALL db.relationshipTypes()"):
        print(record["relationshipType"])

    print("随机节点示例：")
    for record in tx.run("MATCH (n) RETURN n LIMIT 5"):
        print(record["n"])

with driver.session() as session:
    session.read_transaction(check_data)
