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
