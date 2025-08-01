# 🎵 CadastrosMD-Automation 🤖

Automatiza o cadastro de músicas e titulares na plataforma [sistemamd.com.br](https://sistemamd.com.br) por meio da integração com Supabase e automação web com Playwright. Possui upload de planilhas Excel, cadastro automatizado, atualização do status no banco e notificações via Telegram.

---

## 📁 Estrutura do Projeto

| Arquivo/Pasta                             | Descrição                                                                                         |
|------------------------------------------|-------------------------------------------------------------------------------------------------|
| `.env`                                   | Arquivo local para variáveis de ambiente. Nunca versionar este arquivo.                          |
| `.gitignore`                             | Configura o Git para ignorar arquivos sensíveis, como o `.env` e logs.                           |
| `primeiro_codigo_supabase.py`            | Script principal para automação do cadastro via GitHub Actions, usando dados do Supabase.       |
| `segundo_codigo_refatorado.py`           | Script para upload de dados de planilhas Excel para a tabela configurada na Supabase.           |
| `.github/workflows/github_workflow_primeiro.yml` | Workflow que automatiza a execução do cadastro no GitHub Actions.                                 |
| `Emitir.xlsx`                            | Exemplo de planilha Excel com dados de cadastro.                                                |
| `requirements.txt`                       | Lista de dependências Python necessárias para rodar o projeto.                                  |
| `painel_novo.log`                        | Arquivo de log gerado nas execuções para auditoria e debug.                                     |

---

## 🧠 Funcionalidades do Sistema

- 📥 **Upload de planilhas Excel para Supabase:**  
  Leitura inteligente da planilha Excel, normalizando colunas, limpando espaços e importando registros para a tabela configurada. Controla e loga erros para registros inválidos.

- 🤖 **Automação Web com Playwright:**  
  Navega no site sistemamd.com.br, realiza login seguro e cadastra automaticamente cada faixa musical, preenchendo todos os dados necessários.

- 🔄 **Atualização de Status em Tempo Real no Supabase:**  
  Após cada cadastro, atualiza o status do registro no banco: sucesso (`Cadastro OK`) ou falha (`Erro no Cadastro`), permitindo fácil monitoramento.

- 📲 **Notificações Instantâneas via Telegram:**  
  Envia resumo dos processos (quantidade cadastrada, erros e alertas) no canal ou chat configurado, garantindo acompanhamento em tempo real sem precisar acessar o sistema manualmente.

- ⚙️ **Execução Automática via GitHub Actions:**  
  Configuração pronta para disparar a automação periodicamente ou sob demanda, eliminando intervenções manuais e garantindo o fluxo contínuo.

- 📊 **Logs Detalhados em Arquivo:**  
  Registra passo a passo do processo, facilitando a identificação de erros, análise e auditoria.

---

## 🛠️ Requisitos e Configuração

### Ambiente

- Python 3.8 ou superior instalado.
- Conta ativa no Supabase com tabela configurada para armazenar os cadastros (normalmente a tabela chama `cadastros`).
- Credenciais válidas para acesso ao [sistemamd.com.br](https://sistemamd.com.br).
- Bot do Telegram criado com token e chat_id configurados para receber notificações.

### Variáveis de Ambiente — `.env`

Configure um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```


# Credenciais do sistema MD

LOGIN_USERNAME=seu_usuario_md
LOGIN_PASSWORD=sua_senha_md

# Configurações do Telegram para notificações

TELEGRAM_TOKEN=seu_token_telegram
TELEGRAM_CHAT_ID=seu_chat_id_telegram

# Supabase - URL e chave da API

SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_API_KEY=sua_api_key_supabase

# Tabela alvo para os cadastros (padrão: "cadastros")

TABELA=cadastros

# Nome do arquivo da planilha Excel

PLANILHA=Emitir.xlsx

```

> ⚠️ **Importante:** Nunca adicione o arquivo `.env` ao repositório Git. Use `.gitignore` para evitar exposição de credenciais.

---

## 📦 Instalação das Dependências

Recomenda-se criar um ambiente virtual (venv) no Python antes da instalação:

```

python -m venv venv
source venv/bin/activate  \# Linux/macOS
venv\Scripts\activate     \# Windows

```

Em seguida, instale as dependências:

```

pip install -r requirements.txt

```

---

## 📋 Uso Detalhado

### Upload da Planilha Excel para o Supabase

Este passo é usado para importar os dados iniciais ou atualizados da planilha para a base Supabase:

```

python segundo_codigo_refatorado.py

```

- O script verifica a estrutura da tabela no Supabase antes de importar.
- Opção para limpar a tabela antes da importação para evitar duplicidades (pode ser feita manualmente conforme prompts).
- Mostra uma barra de progresso e logs dos registros que falharem.

---

### Executando a Automação de Cadastro no Sistema MD

Esta automação realiza o cadastro efetivo das músicas no sistema por meio do navegador sem interface (headless) usando o Playwright:

```

python primeiro_codigo_supabase.py

```

- Busca os dados que ainda não foram cadastrados (status diferente de "Cadastro OK").
- Realiza login automático com as credenciais.
- Para cada registro, preenche o formulário, submete e atualiza o status no Supabase.
- Envia notificação automática via Telegram ao finalizar.
- As informações detalhadas ficam armazenadas no arquivo `painel_novo.log`.

---

### Automatizando com GitHub Actions

A configuração `.github/workflows/github_workflow_primeiro.yml` já está pronta para rodar a automação dentro do GitHub:

- Personalize as `secrets` do repositório (GitHub secrets) para armazenar as variáveis de ambiente.
- Defina disparos automáticos periódicos (cron) ou manuais (workflow_dispatch).
- Permite rodar tudo em nuvem, sem precisar do seu computador local ligado.

---

## 🧰 Como Funciona Internamente

### Scripts

- **segundo_codigo_refatorado.py:**  
  Usa `pandas` para ler a planilha, limpa os dados, e envia via API REST para a tabela Supabase. Registra falhas de importação e exibe progresso com `tqdm`.

- **primeiro_codigo_supabase.py:**  
  Implementa automação com Playwright para navegar no site, realizar login e preencher formulário para cada registro. Usa API do Supabase para buscar e atualizar status. Possui tratamento robusto de erros e envio de notificações via Telegram.

### Arquivo de Logs

- Utiliza `logging` configurado para gravar tudo no arquivo `painel_novo.log` com timestamps e níveis (INFO, WARNING, ERROR).
- Facilita debug e rastreamento histórico dos eventos.

---

## 🔐 Segurança e Boas Práticas

- Use `.gitignore` para proteger seu `.env` e arquivos sensíveis.
- Nunca coloque credenciais direto no código ou no repositório público.
- Para deploy em nuvem (GitHub Actions), configure variáveis de ambiente como *secrets* no repositório.
- Evite armazenar senhas em texto puro em servidores públicos; considere usar ferramentas seguras como HashiCorp Vault se for escalar.
- Faça backup periódico da planilha original e dos dados importados.

---

## 🤝 Contribuições e Suporte

- Qualquer dúvida, erro ou sugestão, abra uma *issue* no repositório.
- Pull requests são bem-vindos para melhorias ou correções.
- Para suporte mais detalhado, descreva o problema e envie logs de erro.

---

## 📄 Licença

Distribuído sob a licença MIT. Consulte o arquivo LICENSE para detalhes.

---

## 📬 Contato

Para contato rápido, abra uma issue no GitHub ou envie mensagem via Telegram (se configurado).

---

## 🚀 Powered by Supabase + Playwright + GitHub Actions + Telegram Bot

*Sistema de automação para cadastro de faixas musicais com relatórios em tempo real via Telegram.*

**Tecnologias:** Supabase · Playwright · Python · Telegram Bot API · GitHub Actions · Excel

**Funcionalidades:** Upload de Planilhas · Automação Web · Cadastro Automatizado · Atualização de Status · Notificações em Tempo Real · Logs Detalhados
