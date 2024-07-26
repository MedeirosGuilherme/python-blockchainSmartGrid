import tkinter as tk
from tkinter import messagebox
import requests
import json
import os

# Variável global para armazenar o endereço da conta do usuário logado
user_address = None

# Funções para interagir com o servidor
def login():
    username = username_entry.get()
    password = password_entry.get()
    if not username or not password:
        messagebox.showerror("Erro", "Username e Password são obrigatórios")
        return
    response = requests.post('http://127.0.0.1:5000/login', json={'username': username, 'password': password})
    if response.status_code == 200:
        global user_address
        user_address = response.json()['address']
        messagebox.showinfo("Login Bem-Sucedido", f"Endereço da Conta: {user_address}")
        login_frame.pack_forget()
        main_frame.pack()
    else:
        messagebox.showerror("Erro", response.json().get('error', 'Falha ao realizar login'))

def register():
    username = username_entry.get()
    password = password_entry.get()
    if not username or not password:
        messagebox.showerror("Erro", "Username e Password são obrigatórios")
        return
    response = requests.post('http://127.0.0.1:5000/register', json={'username': username, 'password': password})
    if response.status_code == 200:
        global user_address
        user_address = response.json()['address']
        messagebox.showinfo("Registro Bem-Sucedido", f"Endereço da Conta: {user_address}")
        login_frame.pack_forget()
        main_frame.pack()
    else:
        messagebox.showerror("Erro", response.json().get('error', 'Falha ao realizar registro'))

def add_data():
    quantity = quantity_entry.get()
    description = description_entry.get()
    
    if not quantity or not description:
        messagebox.showerror("Erro", "Todos os campos são obrigatórios")
        return
    
    response = requests.post('http://127.0.0.1:5000/transact', json={
        'address': user_address,
        'quantity': quantity,
        'description': description
    })
    
    if response.status_code == 200:
        tx_info = response.json()
        tx_hash = tx_info['transactionHash']
        messagebox.showinfo("Dados Adicionados", f"Transação: {tx_hash}")
        # Salvar hash da transação no arquivo transactions.txt
        dir_path = f'transactions/{user_address}'
        os.makedirs(dir_path, exist_ok=True)
        with open(f'{dir_path}/transactions.txt', 'a') as file:
            file.write(f"Transação: {tx_hash}\n")
    else:
        messagebox.showerror("Erro", "Falha ao adicionar dados")

def get_data():
    tx_hash = tx_hash_entry.get()
    if not tx_hash:
        messagebox.showerror("Erro", "Hash da transação é obrigatório")
        return
    response = requests.post('http://127.0.0.1:5000/get_data', json={'transactionHash': tx_hash})
    if response.status_code == 200:
        data_info = response.json()
        messagebox.showinfo("Dados Recuperados", f"Dados: {data_info['data']}")
    else:
        messagebox.showerror("Erro", "Falha ao recuperar dados")

# Interface gráfica
root = tk.Tk()
root.title("Cliente Blockchain")

# Frame de Login
login_frame = tk.Frame(root)
tk.Label(login_frame, text="Username").grid(row=0)
username_entry = tk.Entry(login_frame)
username_entry.grid(row=0, column=1)

tk.Label(login_frame, text="Password").grid(row=1)
password_entry = tk.Entry(login_frame, show="*")
password_entry.grid(row=1, column=1)

tk.Button(login_frame, text="Login", command=login).grid(row=2, columnspan=2)
tk.Button(login_frame, text="Register", command=register).grid(row=3, columnspan=2)
login_frame.pack()

# Frame Principal
main_frame = tk.Frame(root)

# Campos para adicionar dados
tk.Label(main_frame, text="Quantidade (kWh)").grid(row=0)
quantity_entry = tk.Entry(main_frame)
quantity_entry.grid(row=0, column=1)

tk.Label(main_frame, text="Descrição").grid(row=1)
description_entry = tk.Entry(main_frame)
description_entry.grid(row=1, column=1)

tk.Button(main_frame, text="Adicionar Dados", command=add_data).grid(row=2, columnspan=2)

# Campo para hash da transação e botão para recuperar dados
tk.Label(main_frame, text="Hash da Transação").grid(row=3)
tx_hash_entry = tk.Entry(main_frame)
tx_hash_entry.grid(row=3, column=1)

tk.Button(main_frame, text="Recuperar Dados", command=get_data).grid(row=4, columnspan=2)

main_frame.pack_forget()

root.mainloop()
