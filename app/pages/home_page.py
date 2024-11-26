import solara
import solara.lab as lab
from app.components import (
    show_chat,
)

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

template = """Question: {question}
Answer: Let's think step by step."""

promt = ChatPromptTemplate.from_template(template)

model = OllamaLLM(model = 'llama3.1:8b')

chain = promt | model

message = solara.reactive('')
list_message_user = solara.reactive([])
list_message_chatbot = solara.reactive([])

def send_message(mess: str):
    message.set(mess)
    list_message_user.set(list_message_user.get()+[mess])
    #print(message.value)
@solara.component
def home_page():
    with solara.Div(
        style={
            'height' : '100vh',
        }
    ) as container:
        with solara.Div(
            style= {
                'height' : '70%',
                'border-bottom' : '1px solid #ccc',
                'border-radius' : '5px',
                'shadow' : '0 0 10px rgba(0, 0, 0.1)',
                'overflow-y' : 'auto'
            }
        ) as showchat:
            show_chat(
                list_message_user_reactive = list_message_user,
                mess_reactive=message,
                config_model={
                    'model' : model,
                    'prompt' : promt,
                },
            )
        with solara.Div(
            style={
                'padding' : '10px'
            }
        ) as chat_bot:
            lab.ChatInput(send_callback=send_message)
    