from model.chat.chatbot import Bot
from model.RAG.rag import RAG
from model.web_scraper.web_scraper import load_urls, scrape_pages

import streamlit as st
import tkinter as tk
from tkinter import messagebox

from dotenv import load_dotenv
import os
from streamlit_modal import Modal

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

temperature: float = 1.0
selected_provider: str = "groq"
selected_model: str = "llama3-70b-8192"
selected_language: str = "ES"
api_key: str = os.getenv("OPENAI_API_KEY")

rag: RAG = RAG()
chatbot: Bot = Bot(api_key, selected_model, selected_language)


def start_ui():
    st.markdown(
    """
    <style>
    .stVerticalBlock {
        display: flex;
        flex-direction: column;
    }

    .st-emotion-cache-4zpzjl {
        display: none;
    }

    .st-emotion-cache-jmw8un {
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

    start_side_bar()

    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Escribe tu mensaje...")

    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)

        response = chat(prompt)
        # response = f"Echo: {prompt}"

        with st.chat_message("assistant"):
            st.markdown(response)


def start_side_bar():
    with st.sidebar:
        st.header("Configuración")

        temperature = st.slider(
            label="Temperatura de Respuesta", 
            min_value=0.0, 
            max_value=2.0, 
            value=1.0
        )

        selected_model = AVAILABLE_MODELS.get(
            st.selectbox(
                "Modelo de lenguaje",
                AVAILABLE_MODELS.keys()
            )
        )

        selected_provider = LLM_PROVIDERS.get(selected_model)

        selected_language = AVAILABLE_LANGUAGES.get( 
            st.selectbox(
                "Lenaguaje",
                AVAILABLE_LANGUAGES.keys()
            )
        )

        st.header("Enlaces de Origen")

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

    urls = urls.split("\n")
    urls = [url for url in urls if url.strip()]
    
    with open(SOURCE_URLS_PATH, "w") as file:
        file.write("\n".join(urls))


def reload_knowledge_base():
    """
    Reload the knowledge base with the latest data.
    """

    scrape_pages(DATA_PATH, SOURCE_URLS_PATH)
    rag = RAG(
        data_path=DATA_PATH, 
        chroma_path="db", 
        reload_db=True
    )


def reload_config():
    chatbot = Bot(api_key, selected_model, selected_language)


def chat(message: str) -> str:
    """
    Sends a message to the model and returns the response.

    :param message: The message to send to the model.
    :type message: str
    :return: The response from the model.
    :rtype: str
    """

    st.session_state.messages.append({"role": "user", "content": message})
    
    message = rag.augment_query(message)

    if message == "No data available.":
        return message

    response = chatbot.chat(st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": response})

    return response


start_ui()