from flask import Flask, request, jsonify
from web3 import Web3
import os
import json
import logging
from datetime import datetime

app = Flask(__name__)

# Configuração do logger
log_filename = 'server.log'
logging.basicConfig(filename=log_filename, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Conecte-se ao Ganache
ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

# Verifique se está conectado
if web3.is_connected():
    logging.info("Conectado ao Ganache")
else:
    logging.error("Não foi possível conectar ao Ganache")

# Carregar configurações do servidor
with open('config.json', 'r') as file:
    config = json.load(file)

# Carregar informações dos usuários
if os.path.exists('users.json'):
    with open('users.json', 'r') as file:
        users = json.load(file)
else:
    users = {}

# Função para salvar informações dos usuários
def save_users():
    with open('users.json', 'w') as file:
        json.dump(users, file, indent=4)

# Função para criar um novo nó (conta)
@app.route('/create_account', methods=['POST'])
def create_account():
    account = web3.eth.account.create()
    account_info = {
        'address': account.address,
        'private_key': account._private_key.hex()
    }
    logging.info(f"Conta criada: {account_info}")
    return jsonify(account_info)

# Função para realizar transações de compra/venda
@app.route('/transact', methods=['POST'])
def transact():
    try:
        data = request.json
        account_address = data['address']
        quantity = data['quantity']
        description = data['description']
        
        # Obter preço do config.json
        price = config['price']
        
        # Dados adicionais
        additional_data = f"Quantity: {quantity} kWh, Price: {price} Ether, Description: {description}"
        
        tx_hash = web3.eth.send_transaction({
            'from': web3.eth.accounts[0],  # usando a conta 0 para enviar a transação
            'to': account_address,
            'value': web3.to_wei(price, 'ether'),  # preço da energia
            'data': web3.to_hex(additional_data.encode('utf-8'))
        })
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Salvar a hash da transação com detalhes
        dir_path = f'transactions/{account_address}'
        os.makedirs(dir_path, exist_ok=True)
        with open(f'{dir_path}/transactions.txt', 'a') as file:
            file.write(f"Transação: {receipt.transactionHash.hex()}: {additional_data}\n")
        
        logging.info(f"Transação feita: {data}, Hash: {receipt.transactionHash.hex()}")
        return jsonify({'transactionHash': receipt.transactionHash.hex()})
    except Exception as e:
        logging.error(f"Erro ao realizar transação: {e}")
        return jsonify({'error': str(e)}), 500

# Função para recuperar dados da blockchain
@app.route('/get_data', methods=['POST'])
def get_data():
    try:
        tx_hash = request.json['transactionHash']
        tx = web3.eth.get_transaction(tx_hash)
        data = web3.to_text(tx.input)
        logging.info(f"Dados recuperados: {data}")
        return jsonify({'data': data})
    except Exception as e:
        logging.error(f"Erro ao recuperar dados: {e}")
        return jsonify({'error': str(e)}), 500

# Função de login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    
    if username in users and users[username]['password'] == password:
        logging.info(f"Login bem-sucedido: {username}, Endereço: {users[username]['address']}")
        return jsonify({'address': users[username]['address']})
    else:
        logging.warning(f"Tentativa de login inválida para o usuário: {username}")
        return jsonify({'error': 'Invalid username or password'}), 401

# Função de registro
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']
    
    if username in users:
        logging.warning(f"Tentativa de registro com username já existente: {username}")
        return jsonify({'error': 'Username already exists'}), 400
    
    account = web3.eth.account.create()
    users[username] = {
        'password': password,
        'address': account.address,
        'private_key': account._private_key.hex()
    }
    save_users()
    
    logging.info(f"Usuário registrado: {username}, Endereço: {account.address}")
    return jsonify({'address': account.address})

# Rota para obter a lista de usuários
@app.route('/get_users', methods=['GET'])
def get_users():
    try:
        usernames = list(users.keys())
        logging.info("Usuários carregados")
        return jsonify(usernames)
    except Exception as e:
        logging.error(f"Erro ao carregar usuários: {e}")
        return jsonify({'error': str(e)}), 500

# Rota para obter detalhes de um usuário específico
@app.route('/get_user_details/<username>', methods=['GET'])
def get_user_details(username):
    try:
        if username in users:
            user_info = users[username]
            address = user_info['address']
            
            # Carregar transações do usuário
            transactions_file = f'transactions/{address}/transactions.txt'
            transactions = []
            total_kwh = 0.0
            if os.path.exists(transactions_file):
                with open(transactions_file, 'r') as file:
                    for line in file:
                        transactions.append(line.strip())
                        # Extrair quantidade em kWh da linha da transação
                        if "Quantity" in line:
                            parts = line.split(',')
                            for part in parts:
                                if "Quantity" in part:
                                    quantity_str = part.split(':')[1].strip().split()[0]
                                    try:
                                        total_kwh += float(quantity_str)
                                    except ValueError:
                                        logging.error(f"Erro ao converter quantidade: {quantity_str}")

            # Detalhes do usuário
            user_details = {
                'username': username,
                'address': address,
                'transactions': transactions,
                'total_kwh': total_kwh
            }
            
            logging.info(f"Detalhes do usuário carregados: {user_details}")
            return jsonify(user_details)
        else:
            logging.warning(f"Usuário não encontrado: {username}")
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        logging.error(f"Erro ao carregar detalhes do usuário: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    try:
        app.run(port=5000)
    except Exception as e:
        logging.error(f"Erro ao iniciar o servidor: {e}")
