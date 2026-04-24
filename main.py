from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Optional
import secrets

import os

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./livros.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI(
    title="API de Livros",
    description="Uma API simples para gerenciar uma coleção de livros.",
    version="1.0.0",
    contact={
        "name": "Arthur"
    }
)

# Configurações de autenticação
MEU_USUARIO = os.getenv("MEU_USUARIO")
MINHA_SENHA = os.getenv("MINHA_SENHA")

security = HTTPBasic()

class Livro(BaseModel):
    titulo: str
    autor: str
    ano_publicacao: int


class LivrosDB(Base):
    __tablename__ = "Livros"
    id = Column(Integer, index=True, primary_key=True)
    titulo = Column(String, index=True)
    autor = Column(String, index=True)
    ano_publicacao = Column(Integer)

Base.metadata.create_all(bind=engine)

def sessao_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Função para autenticar o usuário usando HTTP Basic Authentication
# Essa função será usada como dependência em rotas (endpoints) que exigem autenticação
def autenticar_usuario(credentials: HTTPBasicCredentials = Depends(security)):
    is_usuario_valido = secrets.compare_digest(credentials.username, MEU_USUARIO)
    is_senha_valida = secrets.compare_digest(credentials.password, MINHA_SENHA)

    if not (is_usuario_valido and is_senha_valida):
        raise HTTPException(
                            status_code=401,
                            detail="Credenciais inválidas.",
                            headers={"WWW-Authenticate": "Basic"}
        )           

@app.get("/")
def hello_world():
    return {"message": "Hello, World!"}

# Endpoint para obter a lista de livros com suporte a paginação
# O cliente pode especificar os parâmetros 'page' e 'limit' para controlar a paginação dos resultados.
@app.get("/livros/")
def get_livros(page: int = 1, limit: int = 10, db: Session = Depends(sessao_db), sort_by: str = "id", order: str = "asc", credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):

    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Page e limit devem ser maiores que 0.")
    
    if limit > 100:
        raise HTTPException(status_code=400, detail="Limit deve ser no máximo 100.")

    livros = db.query(LivrosDB).offset((page - 1)*limit).limit(limit).all()

    if not livros:
        return {"message": "Nenhum livro encontrado."}

    total_livros =  db.query(LivrosDB).count()

    return {
        "page": page,
        "limit": limit,
        "total": total_livros,
        "livros": [{"id": livro.id, "titulo": livro.titulo, "autor": livro.autor, "ano_publicacao": livro.ano_publicacao} for livro in livros]
    }
            

# id do livro
# nome do livro
# autor do livro
# ano de publicação

@app.post("/adiciona")
def post_livros(livro: Livro, db: Session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
    db_livro = db.query(LivrosDB).filter(LivrosDB.titulo == livro.titulo, LivrosDB.autor == livro.autor).first()
    if db_livro:
        raise HTTPException(status_code=400, detail="Livro já existe.")

    novo_livro = LivrosDB(titulo=livro.titulo, autor=livro.autor, ano_publicacao=livro.ano_publicacao)
    db.add(novo_livro)
    db.commit()
    db.refresh(novo_livro)

    return {"message": "Livro adicionado com sucesso.", "livro": {"id": novo_livro.id, "titulo": novo_livro.titulo, "autor": novo_livro.autor, "ano_publicacao": novo_livro.ano_publicacao}}

@app.put("/atualiza/{id_livro}")
def put_livros(id_livro: int, livro: Livro, db: Session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
    db_livro = db.query(LivrosDB).filter(LivrosDB.id == id_livro).first()
    if not db_livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")

    db_livro.titulo = livro.titulo
    db_livro.autor = livro.autor
    db_livro.ano_publicacao = livro.ano_publicacao
    db.commit()
    db.refresh(db_livro)

    return {"message": "Livro atualizado com sucesso.", "livro": {"id": db_livro.id, "titulo": db_livro.titulo, "autor": db_livro.autor, "ano_publicacao": db_livro.ano_publicacao}}

@app.delete("/deleta/{id_livro}")
def delete_livros(id_livro: int, db: Session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
    db_livro = db.query(LivrosDB).filter(LivrosDB.id == id_livro).first()
    if not db_livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")

    db.delete(db_livro)
    db.commit()

    return {"message": "Livro deletado com sucesso."}