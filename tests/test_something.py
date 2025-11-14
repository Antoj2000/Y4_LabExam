import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app, get_db
from app.models import Base

def author_payload(name="Anthony", email="anto@gmail.com", year_started= 1990):
    return {
        "name" : name,
        "email" : email,
        "year_started": year_started
    }

def book_payload(title="Something", pages= 600, author_id=1):
    return {
        "title" : title,
        "pages" : pages,
        "author_id": author_id
    }

def test_create_author(client):
    r = client.post("/api/authors", json=author_payload())
    assert r.status_code==201

def test_author_dupe(client):
    r = client.post("/api/authors", json=author_payload())
    assert r.status_code==409
    assert r.json()["detail"] == "User already exists"

def  test_delete_then_404(client):
    r = client.post("/api/authors", json = author_payload(email="delete@gmail.com"))
    r = client.delete("/api/authors/2")
    assert r.status_code==204
    r = client.get("/api/users/2")
    assert r.status_code==404

def test_update_author(client):
    r = client.post("/api/authors", json= author_payload(email="update@gmail.com"))
    r = client.put("/api/authors/2", json= author_payload(name="Conor",email="update@gmail.com"))
    assert r.status_code==200
    data = r.json()
    assert data["name"] == "Conor"

def test_create_book(client):
    r = client.post("/api/books", json=book_payload())
    assert r.status_code==201






