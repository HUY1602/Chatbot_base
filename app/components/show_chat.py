import solara
from solara.tasks import use_task, Task
import solara.lab as lab
from langchain_ollama.llms import OllamaLLM

manager = solara.reactive([])

# Hàm gọi AI, chỉ trả về text
def get_ai_chat(chain: OllamaLLM, current_mess: str) -> str:
    if current_mess.strip() == "":
        return "Please enter a message"
    return chain.invoke(current_mess)

# Lấy lại lịch sử chat cũ
def get_old_mess():
    old_mess = []
    for mess in manager.get():
        user_chat = lab.ChatMessage(
            children=[solara.Markdown(md_text=mess['user'])],
            user=True
        )
        ai_chat = lab.ChatMessage(
            children=[solara.Markdown(md_text=mess['ai'])],
            user=False
        )
        old_mess.extend([user_chat, ai_chat])
    return old_mess


@solara.component
def show_chat(
    mess_reactive: solara.Reactive,
    config_model: dict,
    list_message_user_reactive: solara.Reactive,
    list_message_chatbot_reactive: solara.Reactive = None,
):
    chain = config_model['prompt'] | config_model['model']

    # gọi model async
    get_ai_chat_response: Task = use_task(
        lambda: get_ai_chat(chain=chain, current_mess=mess_reactive.value),
        dependencies=[mess_reactive.value]
    )

    # Debug (in ra mỗi lần có message mới)
    solara.use_effect(
        lambda: print("User message:", mess_reactive.value),
        dependencies=[mess_reactive.value]
    )

    old_mess = get_old_mess()

    if get_ai_chat_response.finished:
        ai_mess = get_ai_chat_response.result.value

        # chỉ update manager 1 lần sau khi task xong
        if not manager.get() or manager.get()[-1]["user"] != mess_reactive.value:
            manager.set(manager.get() + [{
                "user": mess_reactive.value,
                "ai": ai_mess
            }])

        return lab.ChatBox(children=[
            *get_old_mess()
        ])

    else:
        # đang chờ AI trả lời → hiển thị user msg + loading
        return lab.ChatBox(children=[
            *old_mess,
            lab.ChatMessage(children=[mess_reactive.value], user=True),
            solara.ProgressLinear(value=get_ai_chat_response.progress)
        ])
