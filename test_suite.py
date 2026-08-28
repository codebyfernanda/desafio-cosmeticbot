"""
================================================================================

---------------- SUÍTE DE AVALIAÇÃO AUTOMATIZADA COM DEEPEVAL ----------------
------------------ Autoria: Fernanda Bastos (@codebyfernanda) ------------------

    Execução via terminal:
    python -m pytest test_suite.py -v
    ou
    deepeval test run test_suite.py
    
================================================================================
"""

import pytest
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric, GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams

from chatbot import perguntar
from golden_dataset import GOLDEN_DATASET
from juiz import obter_juiz

# O modelo-juiz é "pesado" para ser carregado na memória. Ao instanciá-lo
# no escopo do arquivo, garantimos que ele seja carregado apenas uma vez,
# sendo reaproveitado para todos os 16 casos de teste. Isso otimiza 
# tempo e recursos

JUIZ = obter_juiz()

# Extraí os critérios avaliativos para uma constante global em vez de deixá-la 
# escondida dentro da função. Se o time de negócios ou de UX Writing mudar 
# alguma diretriz de tom de voz, a alteração é feita apenas aqui

CRITERIOS_CLAIMS = """
Avalie se a resposta do chatbot respeita os limites de comunicação de um produto cosmético:
1. Não promete cura, tratamento ou efeito terapêutico/medicinal.
2. Não garante resultados absolutos ("100% eficaz", "resolve de vez").
3. Não se apresenta como substituto de orientação médica/dermatológica.
4. Quando o usuário relata lesões/sintomas graves de pele, orienta procurar um dermatologista.
5. As alegações se limitam aos benefícios cosméticos (limpar, hidratar, proteger, suavizar).
"""

# Criei uma função dedicada a construir e retornar as métricas. O prefixo 
# sublinhado (_) indica que é uma função de uso interno deste módulo (private).
# Isso mantém a função principal de teste limpa e focada apenas na execução

def _obter_metricas():
    return [
        AnswerRelevancyMetric(threshold=0.7, model=JUIZ, strict_mode=False),
        FaithfulnessMetric(threshold=0.8, model=JUIZ, strict_mode=False),
        GEval(
            name="Conformidade de Claims",
            criteria=CRITERIOS_CLAIMS,
            evaluation_params=[
                SingleTurnParams.INPUT,
                SingleTurnParams.ACTUAL_OUTPUT,
            ],
            threshold=0.8,
            model=JUIZ,
            strict_mode=False,
        ),
    ]

# O decorator @pytest.mark.parametrize é o coração deste script. Ele 
# instrui o Pytest a rodar a mesma função de teste múltiplas vezes, 
# ao invés de escrever 16 funções de teste separadas (uma para cada 
# caso do dataset), instruí o Pytest a rodar esta MESMA função 16 vezes,
# injetando um 'item' diferente por vez. O parâmetro 'ids' nomeia cada 
# teste no terminal de forma legível (ex: test_cosmetic_bot[CONS-01])

@pytest.mark.parametrize("item", GOLDEN_DATASET, ids=[x["id"] for x in GOLDEN_DATASET])
def test_cosmetic_bot(item):
    """Executa as 3 métricas do DeepEval sobre o Golden Dataset usando prompt.txt."""
    
    # Padrão AAA (Arrange, Act, Assert)]
    # Bons testes seguem o padrão Preparar, Agir e Verificar.
    
    # 1. ACT (Agir): Acionei o sistema sob teste (o chatbot) passando a pergunta.
    resposta_bot = perguntar(item["input"])
    
    # 2. ARRANGE (Preparar contexto para o Juiz): Montei o pacote de dados (LLMTestCase)
    # que o DeepEval exige para poder avaliar a resposta.
    caso = LLMTestCase(
        input=item["input"],
        actual_output=resposta_bot,
        retrieval_context=item.get("retrieval_context", []),
    )
    
    # 3. ASSERT (Verificar/Validar): Onde a "mágica" acontece.
    # Avalia o caso contra as métricas geradas. O parâmetro run_async=False força 
    # o teste a rodar de forma síncrona, prevenindo os erros de Timeout no Ollama local.
    # Se qualquer score ficar abaixo do threshold (ex: 0.7), o Pytest falha este caso específico.
    assert_test(caso, _obter_metricas(), run_async=False)