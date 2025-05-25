from flask import Flask, render_template, request, redirect
import sqlite3
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Criação do banco de dados e tabela
def criar_tabela():
    conn = sqlite3.connect('sapatos.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS sapatos (
            id TEXT PRIMARY KEY,
            modelo TEXT NOT NULL,
            estilo TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Inserção de dados
def inserir_dado(id, modelo, estilo):
    conn = sqlite3.connect('sapatos.db')
    c = conn.cursor()
    c.execute('INSERT INTO sapatos (id, modelo, estilo) VALUES (?, ?, ?)', (id, modelo, estilo))
    conn.commit()
    conn.close()

# Buscar todos os sapatos
def buscar_sapatos():
    conn = sqlite3.connect('sapatos.db')
    c = conn.cursor()
    c.execute('SELECT * FROM sapatos')
    dados = c.fetchall()
    conn.close()
    return dados

# Recomendação por similaridade de estilo
def recomendar(estilo_usuario):
    sapatos = buscar_sapatos()
    estilos = [s[2] for s in sapatos]
    modelos = [s[1] for s in sapatos]

    vectorizer = CountVectorizer().fit_transform(estilos + [estilo_usuario])
    similarity = cosine_similarity(vectorizer)

    similaridades = similarity[-1][:-1]
    indices_ordenados = similaridades.argsort()[::-1]
    
    recomendacoes = []
    for idx in indices_ordenados:
        if similaridades[idx] > 0:
            recomendacoes.append(sapatos[idx])
    
    return recomendacoes

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    id = request.form['id']
    modelo = request.form['modelo']
    estilo = request.form['estilo']
    inserir_dado(id, modelo, estilo)
    return redirect('/')

@app.route('/recomendacao', methods=['POST'])
def recomendacao():
    estilo = request.form['estilo']
    recomendacoes = recomendar(estilo)
    return render_template('recomendacao.html', recomendacoes=recomendacoes)

if __name__ == '__main__':
    criar_tabela()
    app.run(debug=True)

