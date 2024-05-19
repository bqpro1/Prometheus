import base64
from openai import OpenAI
from typing import Optional
import logging
from pydantic import BaseModel
from colorama import Fore, Style

logging.basicConfig(level=logging.INFO)

def GPTcall(api_key: str,
            model_name: str,
            role_message: str,
            user_message: str,
            temperature: float,
            max_tokens: Optional[int] = None,
            schema: Optional[BaseModel] = None,
            image_path: Optional[str] = None,
            max_retries: int = 5,
            json_format: bool = True
            ) -> str:

    client = OpenAI(api_key=api_key)

    if not image_path:
        messages = [{"role": "system",
                     "content": [
                          {"type": "text", "text": role_message}
                    ]},
                    {"role": "user",
                     "content": [
                          {"type": "text", "text": user_message}
                    ]}]
    else: 
        
        def encode_image_(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
            
        base64_image = encode_image_(image_path)
        messages = [{"role": "system",
                     "content": [
                          {"type": "text", "text": role_message}
                    ]},
                    {"role": "user",
                     "content": [
                          {"type": "text", "text": user_message},
                          {
                            "type": "image_url",
                            "image_url": {
                              "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                          },
                    ]}]
    
    
    try_num = 0
    for n in range(max_retries):
        try:
            if json_format:
                raw_response = client.chat.completions.create(
                                                    model=model_name,
                                                    temperature=temperature,
                                                    messages=messages,
                                                    max_tokens=max_tokens,
                                                    response_format={ "type": "json_object" }
                                                    )
            else:
                raw_response = client.chat.completions.create(
                                                    model=model_name,
                                                    temperature=temperature,
                                                    messages=messages,
                                                    max_tokens=max_tokens,
                                                    )
            response = raw_response.choices[0].message.content
            if schema:
                schema.model_validate_json(response)
            return response
        except Exception as e:
                if try_num >= max_retries:
                    logging.info(Fore.RED + Style.BRIGHT + f"Error: {e}")
                    return "Error: max_retries exceeded!"
                else:
                    logging.info(Fore.RED + Style.BRIGHT + f"Error: {e}")
                    try_num += 1
                    logging.info(Fore.YELLOW + Style.BRIGHT + f"Retrying... {try_num}")
                    continue