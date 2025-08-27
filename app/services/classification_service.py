import os
import json
import google.generativeai as genai
from app.core.config import settings

try:
    genai.configure(api_key=settings.GEMINI_API_KEY)
except AttributeError as e:
    print(f"Erro: A variável GEMINI_API_KEY não foi encontrada. Verifique seu arquivo .env. Detalhes :{e}")
    exit()

def get_llm_prompt(text: str) -> str:
    prompt = f"""
    Analise o seguinte comentário de um ouvinte de música e classifique-o.
    O comentário é: "{text}"

    Sua tarefa é retornar um objeto JSON, e NADA MAIS, com a seguinte estrutura:
    {{
      "categoria": "...",
      "tags_funcionalidades": {{ "tag_1": "explicação", "tag_2": "explicação" }},
      "confianca": 0.0
    }}

    Instruções detalhadas:
    1.  **"categoria"**: Classifique o comentário em UMA das seguintes categorias:
        - "ELOGIO": O usuário expressa admiração, satisfação ou feedback positivo.
        - "CRÍTICA": O usuário expressa insatisfação, desapontamento ou feedback negativo.
        - "SUGESTÃO": O usuário propõe uma nova ideia, melhoria ou funcionalidade.
        - "DÚVIDA": O usuário faz uma pergunta ou demonstra incerteza sobre algo.
        - "SPAM": O comentário não tem relação com música ou é propaganda.

    2.  **"tags_funcionalidades"**: Identifique os principais tópicos do comentário.
        - A chave da tag deve ser curta, em snake_case (ex: "qualidade_audio", "letra_musica").
        - O valor deve ser uma breve explicação do que a tag significa no contexto do comentário.
        - Se nenhum tópico específico for identificado, retorne um objeto vazio {{}}.
        - Exemplo: Se o comentário for "A batida dessa música é incrível, mas o autotune estragou a voz do cantor", as tags poderiam ser:
          {{
            "producao_batida": "Comentário positivo sobre a batida da música.",
            "uso_autotune": "Crítica sobre o uso excessivo de autotune."
          }}

    3.  **"confianca"**: Um valor de ponto flutuante (float) entre 0.0 e 1.0, indicando sua confiança na classificação da categoria.

    Retorne APENAS o objeto JSON.
    """
    return prompt

def classify_comment(text: str) -> dict | None:
    if settings.MOCK_AI_SERVICE:
        print("--- MODO MOCK ATIVADO: Retornando resposta simulada ---")
        return {
            "categoria": "MOCK",
            "tags_funcionalidades": { "mock_tag": "Essa é uma resposta simulada."},
            "confianca": 1.0
        }
    
    if not text:
        return None
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = get_llm_prompt(text)

        response = model.generate_content(prompt)

        cleaned_response = response.text.strip().replace("```json", "").replace("```", "").strip()

        result_dict = json.loads(cleaned_response)

        return result_dict
    
    except json.JSONDecodeError:
        print(f"Erro: A resposta da LLM não é um json válido. Resposta: {response.text}")
        return None
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao chamar a API do Gemini: {e}")
        return None