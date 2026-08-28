"""
================================================================================

--------- CONFIG. DO MODELO JUIZ DO DEEPEVAL (UTILIZANDO OLLAMA LOCAL) --------- 
------------------ Autoria: Fernanda Bastos (@codebyfernanda) ------------------

================================================================================
"""

import os
# Importação necessária da classe (OllamaModel) em vez do módulo inteiro, o que 
# economiza memória e deixa claro quais componentes da biblioteca externa 
# são usados

from deepeval.models import OllamaModel


# O verbo "obter" indica claramente uma ação de criação/recuperação.
# A tipagem "-> OllamaModel" garante que chamar essa função saberá 
# exatamente o tipo de objeto que vai receber

def obter_juiz() -> OllamaModel:
    
    # Explica o papel da função no ecossistema da aplicação 
    # (atuar como Juiz): "Retorna uma instância configurada 
    # do OllamaModel para atuar como Juiz no DeepEval"
    
    # Foram usados variáveis de ambiente para que o modelo e 
    # a URL não fiquem fixos no código. O uso de fallbacks 
    # ("llama3.1:8b" e "http://localhost...") garante que o sistema
    # funcione mesmo se alguém esquecer de configurar o arquivo .env.

    modelo = os.getenv("JUIZ_MODEL", os.getenv("LLM_MODEL", "llama3.1:8b"))
    url = os.getenv("OLLAMA_URL", "http://localhost:11434")

    # Útil para debug, informando qual modelo assume o papel de juiz
    print(f"[DeepEval Juiz] Inicializando modelo avaliador: '{modelo}' em '{url}'")

    # Em vez de criar uma variável "juiz = OllamaModel(...)" apenas 
    # para retorná-la na linha de baixo, instanciei o objeto 
    # diretamente, o que reduz a verbosidade e variáveis
    # temporárias desnecessárias

    return OllamaModel(
        model=modelo,
        base_url=url,
    )