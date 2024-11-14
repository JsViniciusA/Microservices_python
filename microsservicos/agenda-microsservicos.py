# servico_contatos.py
import sqlite3
from flask import Flask, request, jsonify

app_contatos = Flask(__name__)

def get_db():
    db = sqlite3.connect('contatos.db')
    db.execute('CREATE TABLE IF NOT EXISTS contatos (id INTEGER PRIMARY KEY, nome TEXT NOT NULL, telefone TEXT NOT NULL, email TEXT NOT NULL)')
    return db

@app_contatos.route('/contatos', methods=['POST'])
def adicionar_contato():
    data = request.json
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO contatos (nome, telefone, email) VALUES (?, ?, ?)', (data['nome'], data['telefone'], (data['email'])))
    db.commit()
    return jsonify({'id': cursor.lastrowid}), 201

@app_contatos.route('/contatos', methods=['GET'])
def listar_contatos():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM contatos')
    contatos = [{'id': row[0], 'nome': row[1], 'telefone': row[2], 'email': row[3]} for row in cursor.fetchall()]
    return jsonify(contatos)

if __name__ == '__main__':
    app_contatos.run(port=4200)

# servico_compromissos.py
import sqlite3
from flask import Flask, request, jsonify
import requests

app_compromissos = Flask(__name__)

def get_db():
    db = sqlite3.connect('compromissos.db')
    db.execute('CREATE TABLE IF NOT EXISTS compromissos (id INTEGER PRIMARY KEY, descricao TEXT NOT NULL, data TEXT NOT NULL, contato_id INTEGER)')
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
        if compromisso['contato_id']:
            response = requests.get(f'  http://localhost:4200/contatos/{compromisso["contato_id"]}')
            if response.status_code == 200:
                compromisso['contato'] = response.json()
    
    return jsonify(compromissos)

if __name__ == '__main__':
    app_compromissos.run(port=4201)

# cliente.py
import requests

def adicionar_contato(self, nome, telefone, email):
    nome = input("Nome do contato: ")
    telefone = input("Telefone do contato: ")
    email = input("Email do contato: ")
    response = requests.post('  http://localhost:4200/contatos', json={'nome': nome, 'telefone': telefone, 'email': email})
    print(f"Contato adicionado com ID: {response.json()['id']}")

def adicionar_compromisso():
    descricao = input("Descrição do compromisso: ")
    data = input("Data do compromisso (YYYY-MM-DD HH:MM): ")
    contato_id = input("ID do contato (opcional): ")
    data = {'descricao': descricao, 'data': data}
    if contato_id:
        data['contato_id'] = int(contato_id)
    response = requests.post('  http://localhost:4201/compromissos', json=data)
    print(f"Compromisso adicionado com ID: {response.json()['id']}")

def listar_contatos():
    response = requests.get('  http://localhost:4201/contatos')
    contatos = response.json()
    for contato in contatos:
        print(f"ID: {contato['id']}, Nome: {contato['nome']}, Telefone: {contato['telefone']}, Email: {contato['email']}")

def listar_compromissos():
    response = requests.get('  http://localhost:4201/compromissos')
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
