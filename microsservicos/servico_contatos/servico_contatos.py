import sqlite3
from flask import Flask, request, jsonify

app_contatos = Flask(__name__)

def get_db():
    db = sqlite3.connect('contatos.db')
    cursor = db.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS contatos (id INTEGER PRIMARY KEY, nome TEXT NOT NULL, telefone TEXT NOT NULL, email TEXT NOT NULL)''')
    db.commit()
    return db

@app_contatos.route('/contatos', methods=['POST'])
def adicionar_contato():
    try:
        data = request.json
        db = get_db()
        cursor = db.cursor()
        print("Dados recebidos:", data)  # Verificar os dados recebidos
        cursor.execute('INSERT INTO contatos (nome, telefone, email) VALUES (?, ?, ?)', (data['nome'], data['telefone'], data['email']))
        db.commit()
        print("Contato adicionado com sucesso")  # Verifica se o commit foi realizado
        return jsonify({'id': cursor.lastrowid}), 201
    except Exception as e:
        print("Erro ao adicionar contato:", e)  # Exibe qualquer erro ocorrido
        return jsonify({'error': str(e)}), 500

@app_contatos.route('/contatos', methods=['GET'])
def listar_contatos():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM contatos')
    contatos = [{'id': row[0], 'nome': row[1], 'telefone': row[2], 'email': row[3]} for row in cursor.fetchall()]
    return jsonify(contatos)

@app_contatos.route('/contatos/<int:contato_id>', methods=['GET'])
def obter_contato(contato_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM contatos WHERE id = ?', (contato_id,))
    row = cursor.fetchone()
    if row:
        contato = {'id': row[0], 'nome': row[1], 'telefone': row[2], 'email': row[3]}
        return jsonify(contato)
    else:
        return jsonify({'error': 'Contato não encontrado'}), 404

if __name__ == '__main__':
    app_contatos.run(host='localhost', port=4200)
