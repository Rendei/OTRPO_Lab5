from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager

from database import Neo4jHandler
from auth import verify_token
from models import Node, NodeWithRelationships
from config import load_config
from fastapi.middleware.cors import CORSMiddleware


config = load_config()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Если neo4j_handler уже был добавлен, пропускаем создание нового
    if not hasattr(app.state, "neo4j_handler"):
        neo4j_handler = Neo4jHandler(config["neo4j_uri"], config["neo4j_user"], config["neo4j_password"])
        app.state.neo4j_handler = neo4j_handler
    yield
    if hasattr(app.state, "neo4j_handler"):
        app.state.neo4j_handler.close()

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/nodes")
def get_all_nodes():
    """Получает все узлы с их id и меткой."""
    return app.state.neo4j_handler.get_all_nodes()

@app.get("/relationships")
async def get_all_relationships():
    return app.state.neo4j_handler.get_all_relationships()

@app.get("/node/{node_id}")
def get_node_with_relationships(node_id: int):
    """Возвращает узел и его связи с атрибутами."""
    return app.state.neo4j_handler.get_node_with_relationships(node_id)

@app.post("/node", dependencies=[Depends(verify_token)])
def add_node_and_relationships(node_with_rels: NodeWithRelationships):
    """Добавляет новый узел и его связи."""
    app.state.neo4j_handler.add_node_and_relationships(
        node_with_rels.node.model_dump(), [rel.model_dump() for rel in node_with_rels.relationships]
    )
    return {"message": "Узел и связи добавлены"}

@app.delete("/node/{node_id}", dependencies=[Depends(verify_token)])
def delete_node_and_relationships(node_id: int):
    """Удаляет узел и его связи."""
    app.state.neo4j_handler.delete_node_and_relationships(node_id)
    return {"message": "Узел и связи удалены"}
