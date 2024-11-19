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

# cliente.py
import requests

class Cliente:
    def __init__(self):
        self.base_url = 'http://localhost:4200'

    def adicionar_contato(self):
        nome = input("Nome do contato: ")
        telefone = input("Telefone do contato: ")
        email = input("Email do contato: ")
        response = requests.post('http://localhost:4200/contatos', json={'nome': nome, 'telefone': telefone, 'email': email})
        print(f"Contato adicionado com ID: {response.json()['id']}")

    def adicionar_compromisso(self):
        descricao = input("Descrição do compromisso: ")
        data = input("Data do compromisso (YYYY-MM-DD HH:MM): ")
        contato_id = input("ID do contato (opcional): ")
        data = {'descricao': descricao, 'data': data}
        if contato_id:
            data['contato_id'] = int(contato_id)
        response = requests.post('http://localhost:4201/compromissos', json=data)
        print(f"Compromisso adicionado com ID: {response.json()['id']}")

    def listar_contatos(self):
        response = requests.get('http://localhost:4200/contatos')
        contatos = response.json()
        for contato in contatos:
            print(f"ID: {contato['id']}, Nome: {contato['nome']}, Telefone: {contato['telefone']}, Email: {contato['email']}")

    def listar_compromissos(self):
        response = requests.get('http://localhost:4201/compromissos')
        compromissos = response.json()
        for compromisso in compromissos:
            contato = compromisso.get('contato', {})
            print(f"ID: {compromisso['id']}, Descrição: {compromisso['descricao']}, Data: {compromisso['data']}, Contato: {contato.get('nome', 'N/A')}")

    # Novo método para pesquisar compromissos por intervalo de datas
    def pesquisar_compromissos(self):
        data_inicio = input("Data de início (YYYY-MM-DD): ")
        data_fim = input("Data de fim (YYYY-MM-DD): ")
        response = requests.get(f'http://localhost:4201/compromissos/pesquisa', params={'data_inicio': data_inicio, 'data_fim': data_fim})
        compromissos = response.json()
        if 'error' in compromissos:
            print(f"Erro: {compromissos['error']}")
        else:
            for compromisso in compromissos:
                contato = compromisso.get('contato', {})
                print(f"ID: {compromisso['id']}, Descrição: {compromisso['descricao']}, Data: {compromisso['data']}, Contato: {contato.get('nome', 'N/A')}")

    def main(self):
        while True:
            print("\n1. Adicionar Contato")
            print("2. Adicionar Compromisso")
            print("3. Listar Contatos")
            print("4. Listar Compromissos")
            print("5. Pesquisar Compromissos por Data")
            print("6. Sair")

            opcao = input("Escolha uma opção: ")

            if opcao == '1':
                self.adicionar_contato()
            elif opcao == '2':
                self.adicionar_compromisso()
            elif opcao == '3':
                self.listar_contatos()
            elif opcao == '4':
                self.listar_compromissos()
            elif opcao == '5':
                self.pesquisar_compromissos()
            elif opcao == '6':
                break
            else:
                print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    cliente = Cliente()
    cliente.main()
