import openai
import logging
from const_config import proxy,openapikey
openai.api_key = openapikey
openai.proxy= proxy['http']
def summarize(message):
    completion =openai.ChatCompletion.create(
    model="gpt-3.5-turbo-0613",
    messages=[{"role": "system", "content": "Summarize the chat in one paragraph from the perspective of assistant and record as much important information as possible from the conversation in chinese"},
              {"role": "user", "content": str(message)}],
)
    logging.info(completion.choices[0]["message"]["content"])
    return completion.choices[0]["message"]["content"]
