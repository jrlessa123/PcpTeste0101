# db_connection.py

import pyodbc
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

def get_db_connection():
    """
    Função para estabelecer e retornar a conexão com o banco de dados SQL Server.
    """
    try:
        # Pega as informações do banco de dados do arquivo .env
        server = os.getenv('DB_SERVER')
        database = os.getenv('DB_DATABASE')
        username = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        driver = '{ODBC Driver 17 for SQL Server}'  # Verifique se este driver está instalado no seu PC

        # Cria a string de conexão
        conn_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
        
        # Tenta conectar ao banco de dados
        conn = pyodbc.connect(conn_string)
        print("Conexão com o banco de dados estabelecida com sucesso!")
        return conn

    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        if sqlstate == '28000':
            print("Erro de autenticação: Usuário ou senha incorretos.")
        else:
            print(f"Erro ao conectar ao banco de dados: {ex}")
        return None

# ----- Exemplo de como usar a função (remova para uso na aplicação) -----
if __name__ == '__main__':
    # Cria o arquivo .env (se não existir) com as suas credenciais
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(f"DB_SERVER=192.168.163.20\n")
            f.write(f"DB_DATABASE=PROTHEUS11\n")
            f.write(f"DB_USER=sa\n")
            f.write(f"DB_PASSWORD=Flamb@2014\n")
    
    conn = get_db_connection()
    if conn:
        conn.close()