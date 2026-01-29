from fastapi import FastAPI, HTTPException

app = FastAPI()

meus_livros = {}

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
def post_livros(id_livro: int, titulo: str, autor: str, ano_publicacao: int):
    if id_livro in meus_livros:
        raise HTTPException(status_code=400, detail="Livro com este ID já existe.")
    else:
        meus_livros[id_livro] = {
            "titulo": titulo,
            "autor": autor,
            "ano_publicacao": ano_publicacao
        }
        return {"message": "Livro adicionado com sucesso.", "livro": meus_livros[id_livro]}
    
@app.put("/atualiza/{id_livro}")
def put_livros(id_livro: int, titulo: str = None, autor: str = None, ano_publicacao: int = None):
    if id_livro not in meus_livros:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")
    else:
        if titulo:
            meus_livros[id_livro]["titulo"] = titulo
        if autor:
            meus_livros[id_livro]["autor"] = autor
        if ano_publicacao:
            meus_livros[id_livro]["ano_publicacao"] = ano_publicacao
        return {"message": "Livro atualizado com sucesso.", "livro": meus_livros[id_livro]}
    
@app.delete("/deleta/{id_livro}")
def delete_livros(id_livro: int):
    if id_livro not in meus_livros:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")
    else:
        deleted_book = meus_livros.pop(id_livro)
        return {"message": "Livro deletado com sucesso.", "livro": deleted_book}