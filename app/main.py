# app/main.py
from typing import Optional

from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Response
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import engine, SessionLocal
from app.models import Base, AuthorDB, BookDB
from app.schemas import (
    AuthorRead, AuthorCreate, AuthorPatch, 
    BookRead, BookCreate, BookPatch)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (dev/exam). Prefer Alembic in production.
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()

def commit_or_rollback(db: Session, error_msg:str):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        HTTPException(status_code=409, detail=error_msg)


# ---- Health ----
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/authors", response_model=AuthorRead, status_code=201)
def create_author(payload:AuthorCreate, db: Session = Depends(get_db)):
    author = AuthorDB(**payload.model_dump())
    db.add(author)
    commit_or_rollback(db,"Author Already Exists")
    db.refresh(author)
    return author

@app.get("/api/authors", response_model=list[AuthorRead], status_code=200)
def list_authors(db: Session = Depends(get_db)):
    stmt = select(AuthorDB).order_by(AuthorDB.id)
    return list(db.execute(stmt).scalars())

@app.get("/api/authors/{author_id}", response_model=AuthorRead)
def get_author(author_id: int, db: Session = Depends(get_db)):
    author = db.get(AuthorDB, author_id)
    if not author:
        raise HTTPException()
    return author

@app.put("/api/authors/{author_id}", response_model=AuthorRead)
def update_author(author_id: int, payload: AuthorCreate, db: Session = Depends(get_db)):
    author = db.get(AuthorDB, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    for key, value in payload.model_dump().items():
        setattr(author, key, value)
    try:
        db.commit()
        db.refresh(author)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Author already exists")
    return author

@app.patch("/api/authors/{author_id}", response_model=AuthorRead)
def patch_author(author_id: int, payload: AuthorPatch, db: Session = Depends(get_db)):
    author = db.get(AuthorDB, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(author, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Author already exists")
    return author


@app.delete("/api/authors/{author_id}", status_code=204)
def delete_author(author_id: int, db: Session = Depends(get_db)):
    author = db.get(AuthorDB, author_id)
    if not author:
        raise HTTPException (status_code=404, detail="Author not found")
    db.delete(author)
    db.commit()


@app.post("/api/books", response_model=BookRead, status_code=201)
def create_book(payload: BookCreate, db: Session = Depends(get_db)):
    author = db.get(AuthorDB, payload.author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    book = BookDB(
        title == payload.title,
        pages == payload.pages,
        author_id == payload.author_id,
    )
    db.add(book)
    commit_or_rollback(db,"Book creation failed")
    db.refresh(book)
    return book


@app.get("/api/books", response_model=list[BookRead], status_code=200)
def list_books(db: Session = Depends(get_db)):
    stmt = select(BookDB).order_by(BookDB.id)
    return list(db.execute(stmt).scalars())

@app.get("/api/books/{book_id}", response_model=BookRead)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.get(BookDB, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book



    





