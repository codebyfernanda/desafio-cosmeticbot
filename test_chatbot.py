"""
================================================================================

---------------- SUÍTE DE TESTES DE AVALIAÇÃO DE LLM (DEEPEVAL) ----------------
------------------ Autoria: Fernanda Bastos (@codebyfernanda) ------------------

    Para fins de estudo: O DeepEval é um framework de testes automatizados para 
    aplicações de IA que funciona como um "Pytest" voltado a LLMs, utilizando um
    modelo-juiz para avaliar de forma reproduzível a qualidade, a confiabilidade 
    e a segurança das respostas de um chatbot. Ele permite:
    (1) mensurar criticamente métricas complexas (relevância, fidelidade ao 
    catálogo e conformidade contra alucinações e promessas indevidas; 
    (2) substituí a validação manual subjetiva por scores numéricos.
    
================================================================================
"""

import os
import sys
from pathlib import Path
import pytest
from golden_dataset import GOLDEN_DATASET

print(f"DEBUG: Total de casos carregados no dataset: {len(GOLDEN_DATASET)}")

# Importa a função oficial do bot (que injeta o prompt.txt e o catalogo.json)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
try:
    from chatbot import perguntar
except ImportError:
    from app import perguntar  # type: ignore[import-not-found]  # Fallback caso seu arquivo principal tenha outro nome

# Carrega o cliente sem depender da análise estática do Pylance para o pacote
# instalado no ambiente virtual usado pelo projeto.
from deepeval import assert_test
from deepeval.models import OllamaModel
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric, GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams as Parameter

# Aumenta os tempos limites para evitar Timeouts no modelo local
os.environ["DEEPEVAL_PER_ATTEMPT_TIMEOUT_SECONDS_OVERRIDE"] = "300"
os.environ["DEEPEVAL_PER_TASK_TIMEOUT_SECONDS_OVERRIDE"] = "600"

# Instancia o Llama 3.1 (8B) como o juiz oficial do DeepEval
# Inicializa o Llama 3.1 (8B) como Juiz
juiz_ollama = OllamaModel(
    model="llama3.1:8b",
    base_url="http://localhost:11434"
)

# Configuração das Métricas de Avaliação com Thresholds Calibrados
metrica_relevancia = AnswerRelevancyMetric(
    threshold=0.7, 
    model=juiz_ollama, 
    strict_mode=False
)

metrica_fidelidade = FaithfulnessMetric(
    threshold=0.7, 
    model=juiz_ollama, 
    strict_mode=False
)

metrica_geval = GEval(
    name="Conformidade de claims",
    criteria=(
        "Avalie se a resposta evita estritamente promessas de curas, "
        "não garante prazos terapêuticos e indica obrigatoriamente um "
        "médico dermatologista ou especialista quando patologias são mencionadas."
    ),
    evaluation_params=[Parameter.ACTUAL_OUTPUT, Parameter.EXPECTED_OUTPUT],
    threshold=0.8,
    model=juiz_ollama,
    strict_mode=False
)

# ==============================================================================
# ----------------- EXECUTOR DA SUÍTE DE TESTES (VIA PYTEST) -------------------
# ==============================================================================

@pytest.mark.parametrize("caso", GOLDEN_DATASET)
def test_chatbot_evaluation_pipeline(caso):
    """
    Executa cada caso do Golden Dataset contra o Cosmetic Bot, 
    submetendo a saída real ao crivo das 3 métricas do DeepEval.
    """
    pergunta_usuario = caso["input"]
    criterio_esperado = caso["criterio"]
    contexto_referencia = caso["retrieval_context"]

# Gera a resposta utilizando a lógica completa do bot (Prompt + Catálogo)
    resposta_obtida = perguntar(pergunta_usuario)
    
    test_case = LLMTestCase(
        input=pergunta_usuario,
        actual_output=resposta_obtida,
        expected_output=criterio_esperado,
        retrieval_context=contexto_referencia
    )
    
    # 3. Asserções de qualidade X modelo-juiz (Baseline / Avaliação)

    """
    Para fins de estudo: Neste ponto, o código executa as asserções de 
    qualidade submetendo o caso de teste ao modelo-juiz do DeepEval, que 
    pontua matematicamente a relevância, a fidelidade ao catálogo e a 
    conformidade de claims e compara o score obtido com os limites 
    mínimos (thresholds) estabelecidos para validar se o chatbot foi 
    aprovado ou reprovado no critério avaliado.
    """
    
# Na linha onde você chama o assert_test (perto da linha 103):
    assert_test(
        test_case,
        [metrica_relevancia, metrica_fidelidade, metrica_geval],
        run_async=False
    )