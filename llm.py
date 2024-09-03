from constants import MAX_TOKENS , TEMPERATURE
import os
import requests

def contruct_prompt(system_prompt:str , user_prompt:str , conversation_history)->str:
    final_prompt = f"""{system_prompt} \n \n
    You strictly follow the instructions given above.\n
    You will also be provided a user query below.\n
    {user_prompt}
    Below is the conversation_history.\n
    {conversation_history}
    Based on the instrcutions given to you and the user query and conversation history understand all of them and give accurate responses.
    """
    return final_prompt 

def get_llm_response(system_prompt, user_prompt, conversation_history) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    prompt_to_llm = contruct_prompt(system_prompt, user_prompt, conversation_history)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        "OpenAI-Organization": os.getenv('ORG_ID')
    }

    data = {
        "model": "gpt-4o-mini",
        "max_tokens": MAX_TOKENS,
        "messages": [{"role": "user", "content": f"{prompt_to_llm}"}],
        "temperature": TEMPERATURE
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        output = response.json()
    except Exception as e:
        print(f"Error Occurred {e}")
        return f"Error Occurred {e}"

    return output['choices'][0]['message']['content']