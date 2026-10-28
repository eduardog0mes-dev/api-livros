from fastapi import FastAPI, HTTPException
import sqlite3
from pydantic import BaseModel
 
app = FastAPI()
 
 
class Livro(BaseModel):
    titulo: str
    autor: str
    paginas: int
    nota: float
 
 
def conectar():
    return sqlite3.connect("livros.db")
 
 
def criar_tabela():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            paginas INTEGER,
            nota REAL
        )
    """)
    conexao.commit()
    conexao.close()
 
 
def listar_livros():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT id, titulo, autor, paginas, nota FROM livros")
    linhas = cursor.fetchall()
    conexao.close()
 
    livros = []
    for linha in linhas:
        livros.append({
            "id": linha[0],
            "titulo": linha[1],
            "autor": linha[2],
            "paginas": linha[3],
            "nota": linha[4],
        })
    return livros
 
 
def cadastrar_livro(titulo, autor, paginas, nota):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "INSERT INTO livros (titulo, autor, paginas, nota) VALUES (?, ?, ?, ?)",
        (titulo, autor, paginas, nota),
    )
    conexao.commit()
    conexao.close()
 
 
def buscar_livro(id_livro):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT id, titulo, autor, paginas, nota FROM livros WHERE id = ?",
        (id_livro,),
    )
    linha = cursor.fetchone()
    conexao.close()
 
    if linha is None:
        return None
 
    return {
        "id": linha[0],
        "titulo": linha[1],
        "autor": linha[2],
        "paginas": linha[3],
        "nota": linha[4],
    }
 
 
def atualizar_livro(id_livro, titulo, autor, paginas, nota):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "UPDATE livros SET titulo = ?, autor = ?, paginas = ?, nota = ? WHERE id = ?",
        (titulo, autor, paginas, nota, id_livro),
    )
    alterados = cursor.rowcount
    conexao.commit()
    conexao.close()
    return alterados > 0
 
 
def apagar_livro(id_livro):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM livros WHERE id = ?", (id_livro,))
    apagados = cursor.rowcount
    conexao.commit()
    conexao.close()
    return apagados > 0
 
 
criar_tabela()
 
 
@app.get("/")
def inicio():
    return {"mensagem": "Olá, API de livros lidos!"}
 
 
@app.get("/livros")
def rota_listar_livros():
    return listar_livros()
 
 
@app.get("/livros/{id_livro}")
def rota_buscar_livro(id_livro: int):
    livro = buscar_livro(id_livro)
    if livro is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return livro
 
 
@app.post("/livros")
def rota_cadastrar_livro(livro: Livro):
    cadastrar_livro(livro.titulo, livro.autor, livro.paginas, livro.nota)
    return {"mensagem": "Livro cadastrado"}
 
 
@app.put("/livros/{id_livro}")
def rota_atualizar_livro(id_livro: int, livro: Livro):
    ok = atualizar_livro(id_livro, livro.titulo, livro.autor, livro.paginas, livro.nota)
    if not ok:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return {"mensagem": "Livro atualizado"}
 
 
@app.delete("/livros/{id_livro}")
def rota_apagar_livro(id_livro: int):
    ok = apagar_livro(id_livro)
    if not ok:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    return {"mensagem": "Livro apagado"}