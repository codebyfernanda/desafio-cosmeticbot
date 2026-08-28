"""
================================================================================

---------------- SCRIPT: INTERFACE DE INTEGRAÇÃO DO COSMETIC BOT --------------- 
------------------ Autoria: Fernanda Bastos (@codebyfernanda) ------------------

    Para fins de estudo: O objetivo deste script é atuar como uma interface de 
    integração (um wrapper) limpa, segura e configurável entre a aplicação em 
    Python (neste caso, a suíte de testes do DeepEval ou o Cosmetic Bot) e o
    modelo de IA que roda localmente na máquina através do Ollama.

    Este código resolve um problema até que "clássico": como conectar um 
    sistema a um serviço externo (a API do LLM) sem amarrar o sistema à 
    complexidade do serviço.

================================================================================
"""

import importlib
import os

# Em vez de permitir que o código quebre silenciosamente mais tarde ao chamar a 
# biblioteca, testei a importação no topo. Se falhar, lançamos um erro explícito 
# e já instruí o possível desenvolvedor sobre como corrigir ("pip install ollama")

try:
    ollama = importlib.import_module("ollama")
except ImportError as exc:
    raise ImportError("The 'ollama' package is required. Install it with: pip install ollama")

# Variáveis declaradas em MAIÚSCULO indicam constantes em Python 
# O uso do `os.getenv` com valores de fallback (padrão) deixa o 
# código flexível para mudanças de ambiente sem precisar alterar
# o código-fonte

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODELO = os.getenv("LLM_MODEL", "llama3.1:8b")
TEMPERATURA = float(os.getenv("LLM_TEMPERATURE", "0.3"))

# Garante que a variável de ambiente necessária para a biblioteca do Ollama 
# use a mesma constante validada anteriormente, evitando discrepâncias

os.environ["OLLAMA_API_BASE"] = OLLAMA_URL

def perguntar(pergunta_usuario: str) -> str:
    
    # A docstring abaixo apenas contextualiza o escopo da função
    """Envia a pergunta ao modelo Ollama configurado via variáveis de ambiente"""
    
    # Esta função faz rigorosamente UMA coisa: envelopa a requisição para o LLM 
    # Ela não imprime nada no terminal, não salva logs no banco de dados e não formata arquivos 

    response = ollama.chat(
        model=MODELO,
        messages=[{"role": "user", "content": pergunta_usuario}],
        options={"temperature": TEMPERATURA}
    )
    
    # Em vez de retornar o dicionário JSON inteiro e obrigar o próximo código a 
    # saber navegar nele, a função extrai e devolve apenas a informação de 
    # valor: a string do texto. Isso meio que "blinda" o resto da aplicação 
    # da complexidade da API do Ollama

    return response["message"]["content"]