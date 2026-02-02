from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional 

app = FastAPI()

meus_livros = {}

class Livro(BaseModel):
    titulo: str
    autor: str
    ano_publicacao: int

@app.get("/")
def hello_world():
    return {"message": "Hello, World!"}

@app.get("/livros/")
def get_livros():
    if not meus_livros:
        return {"message": "Nenhum livro cadastrado."}
    else:
        return {"livros": meus_livros}

# id do livro
# nome do livro
# autor do livro
# ano de publicação

@app.post("/adiciona")
def post_livros(id_livro: int, livro: Livro):
    if id_livro in meus_livros:
        raise HTTPException(status_code=400, detail="Livro com este ID já existe.")
    else:
        meus_livros[id_livro] = livro.model_dump() #livro.dict() foi atualizado para livro.model_dump() na versão mais recente do Pydantic
        return {"message": "Livro adicionado com sucesso.", "livro": meus_livros[id_livro]}
    
@app.put("/atualiza/{id_livro}")
def put_livros(id_livro: int, livro: Livro):
    meu_livro = meus_livros.get(id_livro)
    if id_livro not in meus_livros:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")
    else:
        meus_livros[id_livro] = livro.model_dump() #livro.dict() foi atualizado para livro.model_dump() na versão mais recente do Pydantic
        return {"message": "Livro atualizado com sucesso."}    
    
@app.delete("/deleta/{id_livro}")
def delete_livros(id_livro: int):
    if id_livro not in meus_livros:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")
    else:
        deleted_book = meus_livros.pop(id_livro)
        return {"message": "Livro deletado com sucesso.", "livro": deleted_book}