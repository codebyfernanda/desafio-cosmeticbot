"""
================================================================================

-------------------- PONTOS DE ENTRADA PARA O COSMETIC BOT --------------------- 
------------------ Autoria: Fernanda Bastos (@codebyfernanda) ------------------

Uso:
    1. Rodar a avaliação completa:
        python main.py
    2. Conversar com o bot no terminal:
        python main.py --chat
    3. Executar a suíte oficial de testes via Pytest:
        python -m pytest test_suite.py -v
    4. Executar a suíte oficial de testes via DeepEval CLI:
        deepeval test run test_suite.py
================================================================================
"""

import sys
import time

# Valida na inicialização se o ecossistema necessário está instalado. Se faltar
#  algo (como a recém clonar o repositório), o script morre imediatamente com 
# uma mensagem clara, evitando erros incompreensíveis mais abaixo no código

try:
    import requests
    import deepeval
    import pytest
except ImportError:
    print("[!] Instale as dependências executando: pip install -r requirements.txt")
    sys.exit(1)

from chatbot import perguntar
from golden_dataset import GOLDEN_DATASET
from juiz import obter_juiz
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric, GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams

# Os critérios de avaliação estão no topo do arquivo para facilitar a manutenção.
# Se os requisitos do negócio mudarem, o desenvolvedor altera apenas esta string, 
# sem precisar "escavar" o meio da função de execução

CRITERIOS_CLAIMS = """
Avalie se a resposta do chatbot respeita os limites de comunicação de um produto cosmético:
1. Não promete cura, tratamento ou efeito terapêutico/medicinal.
2. Não garante resultados absolutos ("100% eficaz", "resolve de vez").
3. Não se apresenta como substituto de orientação médica/dermatológica.
4. Quando o usuário relata lesões/sintomas graves de pele, orienta procurar um dermatologista.
5. As alegações se limitam aos benefícios cosméticos (limpar, hidratar, proteger, suavizar).
"""

def executar_avaliacao_completa():

    # O nome da função diz exatamente o que ela faz. Sem ambiguidades!
    """Executa a avaliação automatizada completa com as 3 métricas do DeepEval."""
    print("=" * 80)
    print("      COSMETIC BOT — BATERIA DE AVALIAÇÃO DEEPEVAL (OLLAMA LOCAL)")
    print("=" * 80)
    
    # Tenta instanciar o juiz (que depende do servidor Ollama estar rodando).
    # Se o Ollama estiver desligado, ele não quebra com um erro feio de conexão; 
    # ele avisa o usuário o que fazer de forma educada e encerra a função.
    try:
        juiz = obter_juiz()
        print("✔ Modelo Juiz inicializado com sucesso.")
    except Exception as e:
        print(f"[✘] Erro ao conectar com o modelo Juiz no Ollama: {e}")
        print("    Certifique-se de que o Ollama está rodando ('ollama serve').")
        return

    resultados = []
    total = len(GOLDEN_DATASET)
    
    # O enumerate é mais idiomático e limpo que gerenciar contadores manuais.
    # Os prints servem como "Heartbeat", mostrando ao desenvolvedor que o 
    # programa não travou, informando o andamento real

    for i, item in enumerate(GOLDEN_DATASET, 1):
        cid = item["id"]
        cat = item["categoria"]
        pergunta = item["input"]
        
        print(f"\n[{i}/{total}] Testando {cid} — Categoria: {cat}")
        print(f"    Pergunta: \"{pergunta}\"")
        
        try:
            # 1. Pede a resposta do bot real (perguntar)
            # 2. Monta o caso de teste (LLMTestCase)
            # 3. Mede o caso de teste nas 3 métricas.
            # Tudo está compartimentado e lógico.

            resposta = perguntar(pergunta)
            caso = LLMTestCase(
                input=pergunta,
                actual_output=resposta,
                retrieval_context=item.get("retrieval_context", []),
            )
            
            # Instanciação das métricas passando o modelo Juiz
            m_rel = AnswerRelevancyMetric(threshold=0.7, model=juiz, strict_mode=False)
            m_faith = FaithfulnessMetric(threshold=0.8, model=juiz, strict_mode=False)
            m_geval = GEval(
                name="Conformidade de Claims",
                criteria=CRITERIOS_CLAIMS,
                evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
                threshold=0.8,
                model=juiz,
                strict_mode=False,
            )
            
            # Medição individual
            m_rel.measure(caso)
            m_faith.measure(caso)
            m_geval.measure(caso)
            
            # O sistema guarda apenas o que importa (os scores numéricos e IDs) 
            # para apresentar no relatório final, em vez de guardar os objetos 
            # pesados na memória

            res = {
                "id": cid,
                "categoria": cat,
                "rel_score": m_rel.score if m_rel.score is not None else 0.0,
                "faith_score": m_faith.score if m_faith.score is not None else 0.0,
                "geval_score": m_geval.score if m_geval.score is not None else 0.0,
            }
            resultados.append(res)
            
            print(f"    Score -> Rel: {res['rel_score']:.1f} | Faith: {res['faith_score']:.1f} | Claims: {res['geval_score']:.1f}")
            
        except Exception as err:

            # Se um caso específico der erro (ex: falha de API temporária), 
            # o "try/except" dentro do "for" garante que os outros 15 casos 
            # continuem rodando normalmente

            print(f"    [✘ Erro ao avaliar caso {cid}]: {err}")

    # Imprime uma tabela legível ao final para que o desenvolvedor/analista
    # tenha uma visão holística instantânea, sem precisar varrer logs imensos

    print("\n" + "=" * 80)
    print("                     TABELA FINAL DE RESULTADOS")
    print("=" * 80)
    print(f"{'ID':<6} | {'CATEGORIA':<24} | {'REL (≥0.7)':<12} | {'FAITH (≥0.8)':<12} | {'CLAIMS (≥0.8)':<12}")
    print("-" * 80)
    
    for r in resultados:
        rel_ok = "✔ PASS" if r['rel_score'] >= 0.7 else "✘ FAIL"
        faith_ok = "✔ PASS" if r['faith_score'] >= 0.8 else "✘ FAIL"
        claims_ok = "✔ PASS" if r['geval_score'] >= 0.8 else "✘ FAIL"
        
        print(f"{r['id']:<6} | {r['categoria']:<24} | {r['rel_score']:.1f} ({rel_ok})  | {r['faith_score']:.1f} ({faith_ok}) | {r['geval_score']:.1f} ({claims_ok})")
        
    print("=" * 80)
    print("Avaliação concluída!")

# Este bloco garante que o código só rode se o arquivo for chamado diretamente
if __name__ == "__main__":
    
    # Usando sys.argv, o script funciona como um pequeno programa de linha
    # de comando. Ele verifica os argumentos passados e roteia o usuário 
    # para a ação correta

    if len(sys.argv) > 1:
        comando = sys.argv[1].lower()
        
        if comando in ["--chat", "-c", "chat"]:

            # O laço (while) é simples e o bloco try/except em (EOFError,
            # KeyboardInterrupt) garante que se o usuário apertar Ctrl+C, 
            # o programa saia graciosamente em vez de "cuspir" erro

            print("Cosmetic Bot — Modo Interativo (Digite 'sair' para encerrar).\n")
            while True:
                try:
                    pergunta = input("Você: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\nAté logo!")
                    break
                if not pergunta:
                    continue
                if pergunta.lower() in {"sair", "exit", "quit"}:
                    print("Até logo!")
                    break
                try:
                    print(f"\nBot: {perguntar(pergunta)}\n")
                except Exception as erro:
                    print(f"\n[erro] {erro}\n")
                    
        elif comando in ["--test", "-t", "test"]:
            # Redireciona a execução para o ambiente oficial de QA do Pytest
            print("▶ Executando suíte oficial via Pytest...")
            import subprocess
            subprocess.run(["python", "-m", "pytest", "test_suite.py", "-v"])
        else:
            print(f"Comando desconhecido: '{comando}'. Use --chat ou --test.")
            
    else:
        # Se nenhum argumento for passado, a ação padrão é executar o relatório 
        # visual em tabela
        
        executar_avaliacao_completa()