from model.chat.chatbot import Bot
from model.RAG.rag import RAG
from model.web_scraper.web_scraper import load_urls, scrape_pages
from model.speech.text_to_speech import TextToSpeech

import streamlit as st
import tkinter as tk
from tkinter import messagebox

from dotenv import load_dotenv
import os

load_dotenv()

DATA_PATH: str = "data"
SOURCE_URLS_PATH: str = "source_urls.txt"
SOURCE_URLS: list[str] = load_urls(SOURCE_URLS_PATH)

LLM_PROVIDERS: dict[str, str] = {
    "llama3-70b-8192": "groq",
    "llama3-8b-8192": "groq",
    "llama-3.2-90b-text-preview": "groq",
    "llama-3.2-3b-preview": "groq",
    "gemma2-9b-it": "groq",
    "gemma-7b-it": "groq",
    "gpt-4o": "openai",
    "gpt-3.5": "openai",
}

AVAILABLE_MODELS: dict[str, str] = {
    "Llama 3.1 - 70b" : "llama3-70b-8192",
    "Llama 3.1 - 8b" : "llama3-8b-8192",
    "Llama 3.2 - 90b" : "llama-3.2-90b-text-preview",
    "Llama 3.2 - 3b" : "llama-3.2-3b-preview",
    "Gemma 2 - 9b" : "gemma2-9b-it",
    "Gemma - 7b" : "gemma-7b-it",
    "GPT 4o": "gpt-4o",
    "GPT 3.5": "gpt-3.5 turbo",
}

AVAILABLE_LANGUAGES: dict[str, str] = {
    "Español": "ES", 
    "English": "EN"
}

# temperature: float = 1.0
# selected_provider: str = "groq"
# selected_model: str = "llama3-70b-8192"
# selected_language: str = "ES"
# api_key: str = os.getenv("OPENAI_API_KEY") if selected_provider == "openai" else os.getenv("GROQ_API_KEY")
# print("BOT VERSIÓN", chatbot.MODEL, chatbot.PROVIDER)


def init_config():
    """
    Initialize the configuration of the chatbot.

    Save each configuration parameter in the Streamlit session state to keep the state between Streamlit runs.
    """

    if not "selected_language" in st.session_state:
        st.session_state.selected_language = "ES"

    if not "selected_model" in st.session_state:
        st.session_state.selected_model = "llama3-70b-8192"
    
    if not "selected_provider" in st.session_state:
        st.session_state.selected_provider = LLM_PROVIDERS.get(st.session_state.selected_model)

    if not "temperature" in st.session_state:
        st.session_state.temperature = 1.0

    if not "api_key" in st.session_state:
        st.session_state.api_key = os.getenv("OPENAI_API_KEY") if st.session_state.selected_provider == "openai" else os.getenv("GROQ_API_KEY")

    if not "google_api_key" in st.session_state:
        st.session_state.google_api_key = os.getenv("GOOGLE_CLOUD_API_KEY")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if not "bot" in st.session_state:
        chatbot: Bot = Bot(
            st.session_state.api_key,
            st.session_state.selected_model,
            st.session_state.selected_provider,
            st.session_state.selected_language,
            st.session_state.temperature 
        )
        st.session_state.bot = chatbot
    
    if not "rag" in st.session_state:
        rag: RAG = RAG()
        st.session_state.rag = rag

    if not "text2speech" in st.session_state:
        text2speech: TextToSpeech = TextToSpeech(
            st.session_state.google_api_key,
            st.session_state.selected_language
        )

        st.session_state.text2speech = text2speech


def start_ui():
    """
    Start the Streamlit UI.
    """

    init_config()
    start_side_bar()

    st.markdown(
    """
    <style>
    .stVerticalBlock {
        display: flex;
        flex-direction: column;
    }



    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {
        display: none;
    }

    .st-emotion-cache-janbn0 { 
        text-align: right;
        background-color: #303030;
        max-width: 80%;
        border-radius: 50px;
        color: white;
        margin-left: auto;
        display: flex;
    }

    .st-emotion-cache-4oy321 { 
        text-align: left;
        background-color: #213122;
        max-width: 80%;
        border-radius: 50px;
        color: white;
        margin-right: auto;
        display: flex;
    }

    p {
        padding: 5px;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt: str = st.chat_input("Escribe tu mensaje")

    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)

        response: str = chat(prompt)

        with st.chat_message("assistant"):
            st.markdown(response)

        speech_response(response)


def start_side_bar():
    """
    Start the Streamlit sidebar.

    The sidebar contains the configuration options for the chatbot.
    """

    with st.sidebar:
        st.header("Configuración")

        st.session_state.temperature = st.slider(
            label="Temperatura de Respuesta", 
            min_value=0.0, 
            max_value=2.0, 
            value=1.0
        )

        st.session_state.selected_model = AVAILABLE_MODELS.get(
            st.selectbox(
                "Modelo de lenguaje",
                AVAILABLE_MODELS.keys()
            )
        )

        st.session_state.selected_provider = LLM_PROVIDERS.get(st.session_state.selected_model)

        st.session_state.selected_language = AVAILABLE_LANGUAGES.get( 
            st.selectbox(
                "Lenaguaje",
                AVAILABLE_LANGUAGES.keys()
            )
        )

        if st.button("Recargar Chatbot", key="btn_reload_chatbot"):
            reload_chatbot()

        st.header("Base de Conocimiento")

        save_urls(
            st.text_area(
                "Enlaces de Origen",
                "\n\n".join(SOURCE_URLS),
                height=200
            )
        )

        if st.button("Recargar Base de Conocimiento"):
            reload_knowledge_base()


def save_urls(urls: str):
    """
    Save the URLs to scrape from the given file path.

    :param urls: The URLs to save.
    :type urls: str
    """

    urls_list: list[str] = urls.split("\n")
    urls_list = [url for url in urls_list if url.strip()]
    
    with open(SOURCE_URLS_PATH, "w") as file:
        file.write("\n".join(urls_list))


def reload_knowledge_base():
    """
    Reload the knowledge base with the latest data.
    """

    scrape_pages(DATA_PATH, SOURCE_URLS_PATH)

    rag: RAG = RAG(
        data_path=DATA_PATH, 
        chroma_path="db", 
        reload_db=True
    )

    st.session_state.rag = rag


def reload_chatbot():
    """
    Reload the chatbot with the latest configuration.
    """

    st.session_state.api_key = os.getenv("OPENAI_API_KEY") if st.session_state.selected_provider == "openai" else os.getenv("GROQ_API_KEY")

    chatbot: Bot = Bot(
        st.session_state.api_key,
        st.session_state.selected_model,
        st.session_state.selected_provider,
        st.session_state.selected_language,
        st.session_state.temperature 
    )

    st.session_state.bot = chatbot


def chat(message: str) -> str:
    """
    Sends a message to the model and returns the response.

    :param message: The message to send to the model.
    :type message: str
    :return: The response from the model.
    :rtype: str
    """

    st.session_state.messages.append({"role": "user", "content": message})
    
    message = st.session_state.rag.augment_query(message)
    print("Mensaje a enviar al modelo:", message)

    if message == "No data available.":
        return message

    response: str = st.session_state.bot.chat(message)
    st.session_state.messages.append({"role": "assistant", "content": response})

    return response


def speech_response(response: str):
    """
    Sends a speech response to the user.

    :param response: The text to be spoken.
    :type response: str
    """

    st.session_state.text2speech.speech_response(response)


start_ui()