from neo4j import GraphDatabase
import json

class Neo4jHandler:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()

    def get_all_nodes(self):
        with self.driver.session() as session:
            result = session.run("MATCH (n) RETURN n.id as id, labels(n) as label, n.name as name")
            return [{"id": record["id"], "label": record["label"][0], "name": record["name"]} for record in result]

    def get_all_relationships(self):
        with self.driver.session() as session:
            result = session.run(
            """
            MATCH (n)-[r]->(m)
            RETURN n.id AS start_node_id, type(r) AS relationship_type, m.id AS end_node_id, m {.*} AS end_node
            """)
            return [{"relationship_type": record["relationship_type"],
                     "end_node": record["end_node"]} for record in result]
    
    def get_node_with_relationships(self, node_id):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (n)-[r]->(m) WHERE n.id=$id 
                RETURN n {.*}, type(r) AS relationship_type, m {.*} AS end_node
                """, id=node_id
            )
            relationships = []
            for record in result:
                relationships.append({
                    "node": record["n"],
                    "relationship_type": record["relationship_type"],
                    "end_node": record["end_node"]
                })
            return relationships

    def add_node_and_relationships(self, node, relationships):
        with self.driver.session() as session:
            query = """
            MERGE (n:User {id: $id, name: $name, screen_name: $screen_name, sex: $sex, city: $city})
            WITH n
            UNWIND $relationships as rel
            MATCH (m:User {id: rel.end_node_id})
            MERGE (n)-[r:FOLLOW]->(m)
            """
            session.run(query, id=node["id"], name=node["name"], screen_name=node["screen_name"], 
                        sex=node.get("sex"), city=node.get("city"), relationships=relationships)

    def delete_node_and_relationships(self, node_id):
        with self.driver.session() as session:
            session.run("MATCH (n) WHERE id(n)=$id DETACH DELETE n", id=node_id)
