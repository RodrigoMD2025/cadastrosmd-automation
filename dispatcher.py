import os
import requests
import json
import logging
from dotenv import load_dotenv

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Carrega variáveis de ambiente de um arquivo .env para uso local
load_dotenv()

# Carrega configurações das variáveis de ambiente
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_API_KEY = os.getenv('SUPABASE_API_KEY')
TABELA = os.getenv('TABELA', 'cadastros')
MAX_WORKERS = 4  # Máximo de 4 trabalhadores paralelos
BATCH_SIZE = 250 # Registros por trabalhador

def get_pending_count():
    """Busca a contagem exata de registros pendentes no Supabase."""
    if not all([SUPABASE_URL, SUPABASE_API_KEY]):
        logging.error("URL do Supabase ou Chave da API não configuradas. Verifique as variáveis de ambiente.")
        return 0

    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Prefer": "count=exact"  # Pede ao Supabase para retornar a contagem total
    }
    
    # Apenas consultamos o cabeçalho para obter a contagem, sem baixar os dados
    url = f"{SUPABASE_URL}/rest/v1/{TABELA}?select=id&or=(PAINEL_NEW.is.null,PAINEL_NEW.neq.Cadastro OK)&limit=1"
    
    try:
        # Uma requisição HEAD é mais eficiente, pois só precisamos dos cabeçalhos
        response = requests.head(url, headers=headers)
        response.raise_for_status()
        
        # A contagem está no cabeçalho 'content-range'. Ex: "0-0/1234"
        content_range = response.headers.get("content-range")
        if content_range:
            count = int(content_range.split('/')[-1])
            logging.info(f"Encontrados {count} registros pendentes no Supabase.")
            return count
        else:
            logging.warning("Não foi possível encontrar o cabeçalho 'content-range' para determinar a contagem. Assumindo 0.")
            return 0
            
    except requests.RequestException as e:
        logging.error(f"Erro ao buscar contagem do Supabase: {e}")
        return 0

def main():
    """Função principal para calcular e gerar a matriz de trabalhos para o GitHub Actions."""
    total_records = get_pending_count()
    
    matrix = {"include": []}

    if total_records > 0:
        # Calcula o número de trabalhadores necessários com base na sua regra
        num_workers = (total_records + BATCH_SIZE - 1) // BATCH_SIZE
        num_workers = min(num_workers, MAX_WORKERS)

        logging.info(f"Total de registros: {total_records}. Número de trabalhadores calculado: {num_workers}.")

        # Cria a configuração para cada trabalhador
        for i in range(num_workers):
            offset = i * BATCH_SIZE
            limit = BATCH_SIZE
            matrix["include"].append({
                "worker_id": i + 1,
                "offset": offset,
                "limit": limit,
            })
    else:
        logging.info("Nenhum registro para processar. O workflow não irá iniciar nenhum trabalhador.")

    # Formata a saída para o GitHub Actions
    output_string = json.dumps(matrix)
    logging.info(f"Matriz Gerada: {output_string}")
    
    # Imprime a matriz para que o GitHub Actions possa capturá-la como uma saída do job
    # Este formato é entendido pelo `fromJSON` no workflow
    print(output_string)

if __name__ == "__main__":
    main()
