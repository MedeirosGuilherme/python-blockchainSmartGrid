# manager.py

import tkinter as tk
from tkinter import messagebox
import requests

def load_users():
    response = requests.get('http://127.0.0.1:5000/get_users')
    if response.status_code == 200:
        users_list.delete(0, tk.END)
        for user in response.json():
            users_list.insert(tk.END, user)
    else:
        messagebox.showerror("Erro", "Falha ao carregar usuários")

def load_user_details():
    selected_user = users_list.get(tk.ACTIVE)
    if not selected_user:
        messagebox.showerror("Erro", "Nenhum usuário selecionado")
        return
    
    response = requests.get(f'http://127.0.0.1:5000/get_user_details/{selected_user}')
    if response.status_code == 200:
        user_details = response.json()
        details_text.delete('1.0', tk.END)
        details_text.insert(tk.END, f"Username: {user_details['username']}\n")
        details_text.insert(tk.END, f"Address: {user_details['address']}\n")
        details_text.insert(tk.END, "Transações:\n")
        for tx in user_details['transactions']:
            details_text.insert(tk.END, f"  {tx}\n")
    else:
        messagebox.showerror("Erro", "Falha ao carregar detalhes do usuário")

root = tk.Tk()
root.title("Administração de Usuários")

# Lista de usuários
users_list = tk.Listbox(root)
users_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Botões de ações
buttons_frame = tk.Frame(root)
buttons_frame.pack(side=tk.TOP, fill=tk.X)

load_users_button = tk.Button(buttons_frame, text="Carregar Usuários", command=load_users)
load_users_button.pack(side=tk.LEFT)

load_details_button = tk.Button(buttons_frame, text="Carregar Detalhes", command=load_user_details)
load_details_button.pack(side=tk.LEFT)

# Área de detalhes do usuário
details_text = tk.Text(root)
details_text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

root.mainloop()
