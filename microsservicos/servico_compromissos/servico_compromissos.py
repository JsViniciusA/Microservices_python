import sqlite3
from flask import Flask, request, jsonify
import requests

app_compromissos = Flask(__name__)

def get_db():
    db = sqlite3.connect('compromissos.db')
    db.execute('CREATE TABLE IF NOT EXISTS compromissos (id INTEGER PRIMARY KEY, descricao TEXT NOT NULL, data TEXT NOT NULL, contato_id INTEGER)')
    db.commit()
    return db

@app_compromissos.route('/compromissos', methods=['POST'])
def adicionar_compromisso():
    data = request.json
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO compromissos (descricao, data, contato_id) VALUES (?, ?, ?)',
                   (data['descricao'], data['data'], data.get('contato_id')))
    db.commit()
    return jsonify({'id': cursor.lastrowid}), 201

@app_compromissos.route('/compromissos', methods=['GET'])
def listar_compromissos():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM compromissos')
    compromissos = [{'id': row[0], 'descricao': row[1], 'data': row[2], 'contato_id': row[3]} for row in cursor.fetchall()]

    for compromisso in compromissos:
        contato_id = compromisso.get('contato_id')
        if contato_id:
            try:
                response = requests.get(f'http://localhost:4200/contatos/{contato_id}')
                if response.status_code == 200:
                    compromisso['contato'] = response.json()
                else:
                    compromisso['contato'] = {'error': 'Contato não encontrado'}
            except requests.ConnectionError:
                compromisso['contato'] = {'error': 'Falha na conexão com o serviço de contatos'}
    
    return jsonify(compromissos)


@app_compromissos.route('/compromissos/pesquisa', methods=['GET'])
def pesquisar_compromissos():
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    if not data_inicio or not data_fim:
        return jsonify({'error': 'Parâmetros de data_inicio e data_fim são obrigatórios'}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT * FROM compromissos 
        WHERE data BETWEEN ? AND ?
    ''', (data_inicio, data_fim))

    compromissos = [{'id': row[0], 'descricao': row[1], 'data': row[2], 'contato_id': row[3]} for row in cursor.fetchall()]

    for compromisso in compromissos:
        contato_id = compromisso.get('contato_id')
        if contato_id:
            try:
                response = requests.get(f'http://localhost:4200/contatos/{contato_id}')
                if response.status_code == 200:
                    compromisso['contato'] = response.json()
                else:
                    compromisso['contato'] = {'error': 'Contato não encontrado'}
            except requests.ConnectionError:
                compromisso['contato'] = {'error': 'Falha na conexão com o serviço de contatos'}

    return jsonify(compromissos)

if __name__ == '__main__':
    app_compromissos.run(host='localhost', port=4201)