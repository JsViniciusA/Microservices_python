# servico_contatos.py
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


# servico_compromissos.py
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

    # Obter informações de contato do serviço de contatos
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


# cliente.py
import requests

def __init__(self):
    self.base_url = 'http://localhost:4200'

def adicionar_contato():
    nome = input("Nome do contato: ")
    telefone = input("Telefone do contato: ")
    email = input("Email do contato: ")
    response = requests.post('http://localhost:4200/contatos', json={'nome': nome, 'telefone': telefone, 'email': email})
    print(f"Contato adicionado com ID: {response.json()['id']}")

def adicionar_compromisso():
    descricao = input("Descrição do compromisso: ")
    data = input("Data do compromisso (YYYY-MM-DD HH:MM): ")
    contato_id = input("ID do contato (opcional): ")
    data = {'descricao': descricao, 'data': data}
    if contato_id:
        data['contato_id'] = int(contato_id)
    response = requests.post('http://localhost:4201/compromissos', json=data)
    print(f"Compromisso adicionado com ID: {response.json()['id']}")

def listar_contatos():
    response = requests.get('http://localhost:4200/contatos')
    contatos = response.json()
    for contato in contatos:
        print(f"ID: {contato['id']}, Nome: {contato['nome']}, Telefone: {contato['telefone']}, Email: {contato['email']}")

def listar_compromissos():
    response = requests.get('http://localhost:4201/compromissos')
    compromissos = response.json()
    for compromisso in compromissos:
        contato = compromisso.get('contato', {})
        print(f"ID: {compromisso['id']}, Descrição: {compromisso['descricao']}, Data: {compromisso['data']}, Contato: {contato.get('nome', 'N/A')}")

def main():
    while True:
        print("\n1. Adicionar Contato")
        print("2. Adicionar Compromisso")
        print("3. Listar Contatos")
        print("4. Listar Compromissos")
        print("5. Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            adicionar_contato()
        elif opcao == '2':
            adicionar_compromisso()
        elif opcao == '3':
            listar_contatos()
        elif opcao == '4':
            listar_compromissos()
        elif opcao == '5':
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()
