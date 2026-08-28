# ✸ Cosmetic Bot: Automação em QA e Avaliação de LLM
**Por:** Fernanda Bastos ([@codebyfernanda](https://github.com/codebyfernanda)) | *AWS AI FDE Driven Quality Engineering*

Este repositório contém a arquitetura, a suíte de testes e o pipeline de Quality Assurance (QA) para o **Cosmetic Bot**, um assistente virtual especializado no nicho de beleza e dermocosméticos.

O projeto implementa uma infraestrutura local robusta operando modelos fundacionais via **Ollama** (Llama 3.1 8B), utilizando o framework **DeepEval** e **Pytest** para garantir validação determinística, mitigar alucinações de dados clínicos e auditar a conformidade de respostas por meio da estratégia *LLM-as-a-Judge*.

---

## ✸ Arquitetura do Sistema
O ecossistema foi desenhado de forma modular para separar a lógica de negócio da infraestrutura de avaliação, garantindo manutenibilidade e aplicação de princípios de *Clean Code*.

| Módulo | Responsabilidade |
| --- | --- |
| `chatbot.py` | Gerencia a lógica do assistente, integrando o prompt de sistema com restrições de escopo e o catálogo oficial de produtos (`catalogo.json`). |
| `juiz.py` | Configura o modelo avaliador (Llama 3.1 8B) atuando como *LLM-as-a-Judge*, configurado para evitar vieses cognitivos e avaliar o bot base. |
| `golden_dataset.py` | Matriz de 16 casos de teste divididos em 4 categorias críticas: Consulta Direta, Recomendação por Perfil, Fora de Escopo e Adversariais (Riscos Clínicos). |
| `test_suite.py` | Suíte unitária oficial automatizada, pronta para rodar em pipelines de CI/CD via Pytest. |
| `main.py` | Ponto de entrada unificado (CLI) para geração de relatórios visuais tabulares e execução do modo de chat interativo. |

---

## ✸ Estratégia de Quality Assurance (QA)
A validação de qualidade é orientada por limites rigorosos (*thresholds*) em três métricas centrais, focadas em UX e segurança do usuário:

* **Answer Relevancy (≥ 0.7):** Mensura a capacidade do assistente de compreender e responder diretamente à dor do usuário sem desvios.
* **Faithfulness (≥ 0.8):** Mede a fidelidade ao contexto. Penaliza severamente a alucinação de formulações, preços ou ingredientes que não constam no catálogo.
* **Conformidade de Claims via G-Eval (≥ 0.8):** Avaliação de *guardrails* clínicos. Audita se o modelo evita promessas de cura, recusa a indicação de tratamentos para patologias crônicas e direciona obrigatoriamente o usuário a um médico dermatologista quando necessário.

---

## ✸ Aprendizados de Engenharia e Otimização
Durante o desenvolvimento e a execução dos testes exploratórios, aplicamos soluções de engenharia para gargalos técnicos inerentes ao trabalho com LLMs locais:

* **Engenharia de Prompt e UX Writing:** A baseline do projeto apresentou 100% de falha, incluindo alucinações automotivas e culinárias. A refatoração focou em **isolamento de domínio** e **guardrails clínicos mandatórios** ("Consulte um médico dermatologista"), garantindo uma navegação segura.
* **Estabilidade de Hardware vs. Assincronismo:** A execução assíncrona padrão gerou *Timeouts* por sobrecarga no Ollama local. Seguindo princípios de previsibilidade de software, o processamento de métricas no Pytest foi alterado para síncrono (`run_async=False`), estabilizando a suíte.
* **O Paradoxo do Juiz e a Fadiga Cognitiva:** Modelos menores atuando como juízes tendem a reprovar respostas seguras devido a preciosismo semântico. A string de critérios do G-Eval foi simplificada em diretrizes booleanas curtas para manter o rigor sem inviabilizar a aprovação técnica.
* **Impacto do Controle de Temperatura:** Testes variando a temperatura para extremos (ex: 3.0) saturaram as funções de amostragem do modelo, gerando instabilidade na API, divagações severas e quebras no pipeline. Concluiu-se que, para QA e validação determinística, a fixação entre **0.0 e 0.3** é mandatória.

---

## ✸ Como Executar este Projeto
Certifique-se de ter o Python instalado e o servidor do **Ollama** rodando localmente na sua máquina (`ollama serve`).

**1. Instale as dependências:**

```bash
pip install -r requirements.txt

```

**2. Execute a bateria completa de relatórios (Tabela Visual):**

```bash
python main.py

```

**3. Execute a suíte de testes unitários para CI/CD (Pytest):**

```bash
python -m pytest test_suite.py -v

```

**4. Inicie o chat interativo no terminal (Modo Exploratório):**

```bash
python main.py --chat

```
