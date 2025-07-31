import asyncio
import logging
import os
import requests
import pandas as pd
from playwright.async_api import async_playwright
from tqdm import tqdm
from urllib.parse import quote
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env (para uso local)
load_dotenv()

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt='%d/%m/%Y %H:%M:%S',
    filename='painel_novo.log',
    filemode='w',
)

class WebAutomation:
    def __init__(self):
        self.browser = None
        self.page = None
        # Carrega as variáveis de ambiente
        self.login_username = os.getenv('LOGIN_USERNAME')
        self.login_password = os.getenv('LOGIN_PASSWORD')
        self.telegram_token = os.getenv('TELEGRAM_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_api_key = os.getenv('SUPABASE_API_KEY')
        self.tabela = os.getenv('TABELA', 'cadastros')
        
        # Validação das variáveis obrigatórias
        required_vars = [
            self.login_username, self.login_password, 
            self.telegram_token, self.telegram_chat_id,
            self.supabase_url, self.supabase_api_key
        ]
        if not all(required_vars):
            raise ValueError("Variáveis de ambiente obrigatórias não foram definidas. Verifique o arquivo .env ou as secrets do GitHub")

    def buscar_dados_supabase(self):
        """Busca os dados da tabela no Supabase"""
        try:
            logging.info("Buscando dados do Supabase...")
            
            headers = {
                "apikey": self.supabase_api_key,
                "Authorization": f"Bearer {self.supabase_api_key}",
                "Content-Type": "application/json"
            }
            
            # Busca apenas registros que ainda não foram processados (sem status 'Cadastro OK')
            url = f"{self.supabase_url}/rest/v1/{self.tabela}?select=*&PAINEL_NEW=not.eq.Cadastro OK"
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                dados = response.json()
                if not dados:
                    logging.info("Nenhum registro pendente encontrado no Supabase.")
                    return pd.DataFrame()
                
                df = pd.DataFrame(dados)
                logging.info(f"Encontrados {len(df)} registros para processar no Supabase.")
                return df
            else:
                logging.error(f"Erro ao buscar dados do Supabase: {response.status_code} - {response.text}")
                return pd.DataFrame()
                
        except Exception as e:
            logging.error(f"Erro ao conectar com Supabase: {e}")
            return pd.DataFrame()

    def atualizar_status_supabase(self, isrc, status='Cadastro OK'):
        """Atualiza o status de um registro no Supabase"""
        try:
            headers = {
                "apikey": self.supabase_api_key,
                "Authorization": f"Bearer {self.supabase_api_key}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            }
            
            url = f"{self.supabase_url}/rest/v1/{self.tabela}?ISRC=eq.{isrc}"
            data = {"PAINEL_NEW": status}
            
            response = requests.patch(url, headers=headers, json=data)
            
            if response.status_code != 204:
                logging.warning(f"Erro ao atualizar status do ISRC {isrc}: {response.status_code} - {response.text}")
                return False
            return True
            
        except Exception as e:
            logging.error(f"Erro ao atualizar status do ISRC {isrc}: {e}")
            return False

    async def start_driver(self):
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()

    async def close_driver(self):
        if self.browser:
            await self.browser.close()

    async def login(self):
        logging.info('Logando no Painel...')
        await self.page.goto("https://sistemamd.com.br/login?login_error")

        try:
            await self.page.fill('input#login-username', self.login_username)
            await self.page.fill('input#login-password', self.login_password)
            await self.page.click('button[type="submit"]')
            
            # Aguarda um pouco para verificar se o login foi bem-sucedido
            await self.page.wait_for_timeout(2000)
            
            # Verifica se ainda está na página de login (indicaria erro)
            current_url = self.page.url
            if "login" in current_url:
                logging.error("Login falhou - ainda na página de login")
                return False
                
            logging.info("Login realizado com sucesso.")
            return True
        except Exception as e:
            logging.error(f"Erro ao tentar logar: {e}")
            return False

    async def run_task_with_time_estimate(self):
        # Busca dados do Supabase ao invés da planilha
        tabela = self.buscar_dados_supabase()
        
        if tabela.empty:
            logging.info("Nenhum dado para processar. Finalizando...")
            return

        await self.start_driver()
        if not await self.login():
            await self.close_driver()
            return

        total_items = len(tabela)
        contador = 0
        logging.info(f"Iniciando Cadastro de {total_items} Faixas...")

        for index, row in tqdm(tabela.iterrows(), total=total_items, desc="Progresso"):
            try:
                # Ajuste os nomes das colunas conforme sua tabela do Supabase
                isrc = row.get('ISRC')
                artista = row.get('ARTISTA') 
                titulares = row.get('TITULARES')

                if not all([isrc, artista, titulares]):
                    logging.warning(f"Dados incompletos na linha {index}: ISRC={isrc}, ARTISTA={artista}, TITULARES={titulares}")
                    continue

                await self.page.goto("https://sistemamd.com.br/musicas/add")
                await self.page.wait_for_selector('input#titulo')
                await self.page.fill('input#titulo', str(artista))
                await self.page.fill('input#isrc', str(isrc))
                await self.page.click('span.select2-selection')
                titular_input = await self.page.wait_for_selector('input.select2-search__field')
                await titular_input.fill(str(titulares))
                await titular_input.press('Enter')
                await self.page.wait_for_timeout(500)

                await self.page.click('input#titular_2')
                await self.page.click('input#titular_1')
                await self.page.click('input#titular_4')
                await self.page.click('input#titular_5')
                await self.page.click('input#titular_3')

                await self.page.wait_for_timeout(500)
                await self.page.click('button#AdicionarTitular')
                await self.page.click('button#BtnSalvar')

                # Atualiza o status no Supabase ao invés da planilha
                if self.atualizar_status_supabase(isrc, 'Cadastro OK'):
                    logging.info(f"ISRC: {isrc}, Artista: {artista}, Titulares: {titulares} - Status atualizado")
                    contador += 1
                else:
                    logging.warning(f"ISRC: {isrc} - Cadastro realizado mas erro ao atualizar status")
                    
            except Exception as e:
                logging.error(f"Erro durante o cadastro da faixa {index + 1} - ISRC: {isrc}: {e}")
                # Marca como erro no Supabase
                self.atualizar_status_supabase(isrc, 'Erro no Cadastro')
                continue

        logging.info(f"Total de {contador} faixas cadastradas com sucesso.")
        await self.send_telegram_notification(contador)
        await self.close_driver()

    async def send_telegram_notification(self, contador):
        logging.info("Enviando notificação por Telegram...")
        message = f'Painel New Concluído com êxito 👍🏼📝✅\n{contador} arquivo(s) cadastrado(s).\nPor gentileza validar relatório de logs, Obrigado!'
        response = requests.get(
            url=f'https://api.telegram.org/bot{self.telegram_token}/sendMessage?chat_id={self.telegram_chat_id}&text={quote(message)}'
        )
        if response.status_code == 200:
            logging.info("Telegram enviado com sucesso.")
        else:
            logging.error("Erro ao enviar notificação por Telegram.")

async def main():
    try:
        web_automation = WebAutomation()
        logging.info("Iniciando automação com dados do Supabase...")
        await web_automation.run_task_with_time_estimate()
    except ValueError as e:
        logging.error(f"Erro de configuração: {e}")
    except Exception as e:
        logging.error(f"Erro inesperado: {e}")

if __name__ == "__main__":
    asyncio.run(main())