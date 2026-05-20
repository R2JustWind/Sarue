from respostas import llama_answer, qwen_answer
from juiz import judge_prompt, llama_judge, qwen_judge
import json

def avaliar_individual_qwen(pergunta, ref, resposta, secao=None, fonte=None):
    prompt = judge_prompt(pergunta=pergunta, resposta_ref=ref, resposta_modelo=resposta, secao=secao, fonte=fonte)

    julgamento = llama_judge(prompt)

    try:
        return json.loads(julgamento)
    except:
        print("Erro:", julgamento)
        return None
    
def avaliar_individual_llama(pergunta, ref, resposta, secao=None, fonte=None):
    prompt = judge_prompt(pergunta=pergunta, resposta_ref=ref, resposta_modelo=resposta, secao=secao, fonte=fonte)

    julgamento = qwen_judge(prompt)

    try:
        return json.loads(julgamento)
    except:
        print("Erro:", julgamento)
        return None

def avaliar_dataset(dataset):
    resultado = []

    for item in dataset:
        q = item["pergunta"]
        ref = item["resposta"]
        secao = item.get("secao")
        fonte = item.get("fonte")

        ans_llama = llama_answer(q)
        ans_qwen = qwen_answer(q)

        eval_llama = avaliar_individual_llama(q, ref, ans_llama, secao, fonte)
        eval_qwen = avaliar_individual_qwen(q, ref, ans_qwen, secao, fonte)

        resultado.append({
            "pergunta": q,
            "resposta_ref": ref,
            "avaliacao_llama": eval_llama,
            "avaliacao_qwen": eval_qwen,
        })

    return resultado