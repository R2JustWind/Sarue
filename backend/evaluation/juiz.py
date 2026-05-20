from respostas import llama_answer, qwen_answer
import json

def llama_judge(prompt):
    return llama_answer(prompt)

def qwen_judge(prompt):
    return qwen_answer(prompt)

def judge_prompt(pergunta, resposta_modelo, resposta_ref, secao, fonte):
    return f"""
Você é um avaliador rigoroso e imparcial.

Sua tarefa é comparar duas respostas com base em uma resposta de referência confiável.

## Pergunta:
{pergunta}

## Resposta de Referência (verdade esperada):
{resposta_ref}

## Resposta do Modelo a ser Avaliado:
{resposta_modelo}

## Contexto adicional:
Seção: {secao}
Fonte: {fonte}

---

## Critérios (nota de 0 a 5):

1. Correção:
A resposta está correta em relação à referência?

2. Completude:
A resposta cobre as informações principais?

3. Clareza:
A resposta é bem escrita e compreensível?

4. Fidelidade:
A resposta evita inventar informações?

---

## Instruções:
- Dê uma nota de 0 a 5 para cada critério
- Seja rigoroso
- Justifique brevemente

---

## Saída (JSON):

{{
  "correcao": 0-5,
  "completude": 0-5,
  "clareza": 0-5,
  "fidelidade": 0-5,
  "nota_final": 0-5,
  "justificativa": "..."
}}

Responda apenas com JSON válido.
"""

def avaliar_com_juizes(prompt):
    resultado_llama = llama_judge(prompt)
    resultado_qwen = qwen_judge(prompt)

    try:
        eval_llama = json.loads(resultado_llama)
    except:
        eval_llama = None

    try:
        eval_qwen = json.loads(resultado_qwen)
    except:
        eval_qwen = None

    return {
        "llama": eval_llama,
        "qwen": eval_qwen
    }