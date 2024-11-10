import os
import sys
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock,  patch

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from config import load_config
from main import app
from models import Node, NodeWithRelationships, Relationship

config = load_config()
auth_token = config["auth_token"]

# Создаем фикстуру для клиента
@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

# Мокаем Neo4jHandler для тестов
@pytest.fixture(autouse=True)
def mock_neo4j_handler(monkeypatch):
    mock_handler = MagicMock()
    # Мокаем методы, чтобы они возвращали предсказуемые значения
    mock_handler.get_all_nodes.return_value = [
        {"id": 0, "label": "User"},
        {"id": 1, "label": "Group"},
        {"id": 2, "label": "User"}
    ]
    mock_handler.get_node_with_relationships.return_value = {
        "id": 0,
        "label": "User",
        "relationships": [
            {"type": "FOLLOWS", "end_node_id": 2}
        ]
    }
    mock_handler.add_node_and_relationships.return_value = None
    mock_handler.delete_node_and_relationships.return_value = None
    app.state.neo4j_handler = mock_handler
    return mock_handler

# Тест для получения всех узлов
def test_get_all_nodes(client):
    response = client.get("/nodes")
    assert response.status_code == 200
    assert response.json() == [
        {"id": 0, "label": "User"},
        {"id": 1, "label": "Group"},
        {"id": 2, "label": "User"}
    ]

# Тест для получения узла с его связями
def test_get_node_with_relationships(client):
    node_id = 0
    response = client.get(f"/node/{node_id}")
    assert response.status_code == 200
    assert response.json() == {
        "id": node_id,
        "label": "User",
        "relationships": [
            {"type": "FOLLOWS", "end_node_id": 2}
        ]
    }

# Тест для добавления узла и связей
def test_add_node_and_relationships(client):
    node = Node(id=3, label="User", name="Арсений", screen_name="rendei", sex=2, city="Тюмень")
    relationships = [Relationship(type="FOLLOWS", end_node_id=2)]
    node_with_rels = NodeWithRelationships(node=node, relationships=relationships)
    print(node_with_rels.model_dump())
    
    response = client.post("/node", json=node_with_rels.model_dump(), headers={"token": auth_token})
    assert response.status_code == 200
    assert response.json() == {"message": "Узел и связи добавлены"}

# Тест для удаления узла и связей
def test_delete_node_and_relationships(client):
    node_id = 3

    response = client.delete(f"/node/{node_id}", headers={"token": auth_token})
    assert response.status_code == 200
    assert response.json() == {"message": "Узел и связи удалены"}


def test_verify_token_invalid(client):
    response = client.post("/node", headers={"token": "invalid_token"})
    assert response.status_code == 403
    assert response.json() == {"detail": "Недействительный токен"}