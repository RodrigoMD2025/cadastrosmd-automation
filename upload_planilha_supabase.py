import pandas as pd
import requests
import logging
import os
from datetime import datetime
from tqdm import tqdm
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Carrega configurações das variáveis de ambiente
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_API_KEY = os.getenv('SUPABASE_API_KEY')
TABELA = os.getenv('TABELA', 'cadastros')  # valor padrão
PLANILHA = os.getenv('PLANILHA', 'Emitir.xlsx')  # valor padrão

# Validação das variáveis obrigatórias
if not all([SUPABASE_URL, SUPABASE_API_KEY]):
    raise ValueError("Variáveis de ambiente SUPABASE_URL e SUPABASE_API_KEY são obrigatórias. Verifique o arquivo .env")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

headers = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

def verificar_estrutura_tabela():
    """Verifica a estrutura da tabela no Supabase"""
    try:
        # Tenta fazer uma consulta simples para ver a estrutura
        url = f"{SUPABASE_URL}/rest/v1/{TABELA}?limit=1"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            logging.info("Conexão com Supabase estabelecida com sucesso.")
            return True
        else:
            logging.error(f"Erro ao conectar com Supabase: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logging.exception(f"Erro ao verificar estrutura da tabela: {e}")
        return False

def limpar_tabela():
    """Limpa todos os registros da tabela no Supabase"""
    try:
        # Usa ISRC (que existe em todos os registros) ao invés de id
        url = f"{SUPABASE_URL}/rest/v1/{TABELA}?ISRC=neq."
        response = requests.delete(url, headers=headers)
        
        if response.status_code != 204:
            logging.error(f"Erro ao limpar tabela: {response.status_code} - {response.text}")
        else:
            logging.info("Tabela limpa com sucesso.")
    except Exception as e:
        logging.exception(f"Erro ao tentar limpar a tabela: {e}")

def upload_planilha():
    """Faz upload dos dados da planilha para o Supabase"""
    try:
        # Lê a planilha Excel
        df = pd.read_excel(PLANILHA)
        
        # Mostra a estrutura original da planilha
        logging.info(f"Colunas encontradas na planilha: {list(df.columns)}")
        
        # Normaliza os nomes de colunas para MAIÚSCULAS
        df.columns = [col.upper().strip() for col in df.columns]
        logging.info(f"Colunas após normalização: {list(df.columns)}")
        
        logging.info(f"Importando {len(df)} registros para Supabase...")
        
        # Contador de sucessos e erros
        sucessos = 0
        erros = 0
        
        # Barra de progresso com TQDM
        with tqdm(total=len(df), desc="Importando", unit="registro") as pbar:
            # Itera sobre cada linha da planilha
            for index, row in df.iterrows():
                dados = row.dropna().to_dict()
                
                # Remove espaços extras dos valores string
                dados_limpos = {}
                for key, value in dados.items():
                    if isinstance(value, str):
                        dados_limpos[key] = value.strip()
                    else:
                        dados_limpos[key] = value
                
                # Faz a requisição POST para inserir os dados
                response = requests.post(f"{SUPABASE_URL}/rest/v1/{TABELA}", headers=headers, json=dados_limpos)
                
                if response.status_code != 201:
                    erros += 1
                    # Atualiza a descrição da barra com erro
                    pbar.set_postfix({"✅": sucessos, "❌": erros, "Último": f"ERRO - {dados_limpos.get('ISRC', 'N/A')}"})
                    logging.warning(f"Erro ao subir registro {index + 1} - ISRC {dados_limpos.get('ISRC', 'N/A')}: {response.text}")
                else:
                    sucessos += 1
                    # Atualiza a descrição da barra com sucesso
                    pbar.set_postfix({"✅": sucessos, "❌": erros, "Último": dados_limpos.get('ISRC', 'N/A')})
                
                # Atualiza a barra de progresso
                pbar.update(1)
        
        logging.info(f"Importação finalizada: {sucessos} sucessos, {erros} erros")
                
    except FileNotFoundError:
        logging.error(f"Arquivo {PLANILHA} não encontrado.")
    except Exception as e:
        logging.exception(f"Erro ao fazer upload da planilha: {e}")

if __name__ == "__main__":
    try:
        logging.info("Iniciando processo de importação...")
        
        # Verifica se consegue conectar com o Supabase
        if not verificar_estrutura_tabela():
            logging.error("Não foi possível conectar com o Supabase. Verifique as configurações.")
            exit(1)
        
        # Pergunta se deve limpar a tabela
        print(f"\nPlanilha encontrada: {PLANILHA}")
        print(f"Tabela de destino: {TABELA}")
        print(f"URL do Supabase: {SUPABASE_URL}")
        resposta = input("\nDeseja limpar a tabela antes de importar? (s/n): ").lower().strip()
        if resposta in ['s', 'sim', 'y', 'yes']:
            print("Limpando tabela...")
            limpar_tabela()
        
        upload_planilha()
        logging.info("Processo de importação finalizado.")
        
    except ValueError as e:
        logging.error(f"Erro de configuração: {e}")
    except Exception as e:
        logging.error(f"Erro inesperado: {e}")