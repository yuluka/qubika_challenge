from model.chat.chatbot import Bot
from model.RAG.rag import RAG
from model.web_scraper.web_scraper import load_urls, scrape_pages
from model.speech.text_to_speech import TextToSpeech

import streamlit as st
import tkinter as tk
from tkinter import messagebox

from dotenv import load_dotenv
import os
import json

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

AVAILABLE_VOICE_GENDERS: dict[str, str] = {
    "Masculino": "male",
    "Femenino": "female"
}

AVAILABLE_VOICES: dict[str, list[str]] = {
    "male": [
        "es-US-Neural2-B", "es-US-Neural2-C", "es-US-News-D", "es-US-News-E", "es-US-Polyglot-1",
        "es-US-Standard-B", "es-US-Standard-C", "es-US-Studio-B", "es-US-Wavenet-B", "es-US-Wavenet-C",
        "en-US-Casual-K", "en-US-Journey-D", "en-US-Neural2-A", "en-US-Neural2-D", "en-US-Neural2-I",
        "en-US-Neural2-J", "en-US-News-N", "en-US-Polyglot-1", "en-US-Standard-A", "en-US-Standard-B",
        "en-US-Standard-D", "en-US-Standard-I", "en-US-Standard-J", "en-US-Studio-Q", "en-US-Wavenet-A",
        "en-US-Wavenet-B", "en-US-Wavenet-D", "en-US-Wavenet-I", "en-US-Wavenet-J"
    ],
    "female": [
        "es-US-Neural2-A", "es-US-News-F", "es-US-News-G", "es-US-Standard-A", "es-US-Wavenet-A",
        "en-US-Journey-F", "en-US-Journey-O", "en-US-Neural2-C", "en-US-Neural2-E", "en-US-Neural2-F", 
        "en-US-Neural2-G", "en-US-Neural2-H", "en-US-News-K", "en-US-News-L", "en-US-Standard-C", 
        "en-US-Standard-E", "en-US-Standard-F", "en-US-Standard-G", "en-US-Standard-H", "en-US-Studio-O", 
        "en-US-Wavenet-C", "en-US-Wavenet-E", "en-US-Wavenet-F", "en-US-Wavenet-G", "en-US-Wavenet-H"
    ]
}

COMPARISON_NEWS_PATH: str = "data/comparison"

SUMARIZATION_NEWS_CONTEXT: str = """
Tu tarea es resumir el siguiente texto (contenido scrapeado de una página web de una noticia): \n{page_content}

Por favor, sigue estas instrucciones al pie de la letra:

1. **Resumen de la noticia**: Resumir el contenido del texto en un párrafo de 3 a 5 oraciones y extraer la lista de puntos clave.
2. **Sin contenido adicional:** No incluir ningún texto, comentario o explicación adicional en la respuesta.
3. **Respuesta vacía:** Si no puedes resumir la noticia, devuelve una cadena vacía ('').
4. **Sólo datos directos:** Tu salida debe contener sólo los datos solicitados explícitamente, sin ningún otro texto.
5. **Formato de salida:** La salida debe estar en el siguiente formato: 
```
Resumen: 

«Resumen de la noticia aquí»

Puntos clave:

«Lista de puntos clave aquí»
```
"""

def init_config():
    """
    Initialize the configuration of the chatbot.

    Save each configuration parameter in the Streamlit session state to keep the state between Streamlit runs.
    """

    if "current_screen" not in st.session_state:
        st.session_state.current_screen = "main"   

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


    if not "google_api_key" in st.session_state:
        st.session_state.google_api_key = os.getenv("GOOGLE_CLOUD_API_KEY")

    if not "selected_voice_gender" in st.session_state:
        st.session_state.selected_voice_gender = "male"

    if not "selected_voice" in st.session_state:
        st.session_state.selected_voice = "es-US-Wavenet-B"

    if not "text2speech" in st.session_state:
        text2speech: TextToSpeech = TextToSpeech(
            st.session_state.google_api_key,
            st.session_state.selected_language,
            st.session_state.selected_voice,
            st.session_state.selected_voice_gender
        )

        st.session_state.text2speech = text2speech


def start_ui():
    """
    Start the Streamlit UI.
    """

    init_config()

    st.markdown(
    """
    <style>
    .stVerticalBlock {
        display: flex;
        flex-direction: column;
    }

    .st-key-go_to_comparison {
        display: inline-flex;
        justify-content: center;
        position: fixed;
        z-index: 9999;
    }

    .st-key-btn_compare {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 105px;
        margin: auto;
        margin-top: 10px;
    }

    .st-key-btn_read_summary1, .st-key-btn_read_summary2 {
        display: flex;
        width: 46px;
        margin-left: auto;
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

    .comparison-bubble {
        display: inline-block;
        background-color: #00bcd4;
        color: white; 
        padding: 10px 20px;
        border-radius: 50px;
        text-align: center; 
        font-size: 16px; 
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); 
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
    
    if st.button("", key="go_to_comparison", icon=":material/text_compare:"):
        st.session_state.current_screen = "comparison" if st.session_state.current_screen == "main" else "main"

    if st.session_state.current_screen == "main":
        start_main_window()
    elif st.session_state.current_screen == "comparison":
        start_comparison_window()


def start_main_window():
    """
    Start the main window of the Streamlit UI.

    The main window contains the chatbot and the configuration options for the chatbot.
    """

    start_main_side_bar()

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

        speech_response(response, st.session_state.text2speech)


def start_main_side_bar():
    """
    Start the Streamlit sidebar for the main window.

    The sidebar contains the configuration options for the chatbot in the main window.
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

        st.header("Configuración de Voz")
        
        st.session_state.selected_voice_gender = AVAILABLE_VOICE_GENDERS.get(
            st.selectbox(
                "Género de Voz",
                AVAILABLE_VOICE_GENDERS
            )
        )
        
        voices: list[str] = AVAILABLE_VOICES.get(st.session_state.selected_voice_gender, [])
        voices = [voice for voice in voices if voice[:2] == st.session_state.selected_language.lower()]

        st.session_state.selected_voice = AVAILABLE_VOICES.get(
            st.selectbox(
                "Voz",
                voices
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


def start_comparison_window():
    """
    Start the comparison window of the Streamlit UI.

    The comparison window contains the mechanism for comparing two news articles and the configuration options for the comparison chatbot.
    """

    start_comparison_side_bar()

    col1, col2 = st.columns(2)

    col1.write("<h2 style='text-align: center;'>Noticia 1</h2>", unsafe_allow_html=True)
    col2.write("<h2 style='text-align: center;'>Noticia 2</h2>", unsafe_allow_html=True)

    if "summarization1" in st.session_state and "summarization2" in st.session_state:
        render_comparison_results(col1, col2, st.session_state.summarization1, st.session_state.summarization2)

    if st.button("Comparar", key="btn_compare"):
        response1: str = "No se han proporcionado noticias para comparar."
        response2: str = "No se han proporcionado noticias para comparar."

        if st.session_state.news1 != "" and st.session_state.news2 != "":
            print("Scraping news...", st.session_state.news1, st.session_state.news2)
            try:
                scraping_result: bool = scrape_pages(COMPARISON_NEWS_PATH, [st.session_state.news1, st.session_state.news2], False)

                if scraping_result:
                    news1: dict = load_json(f"{COMPARISON_NEWS_PATH}/output_0.json")
                    news2: dict = load_json(f"{COMPARISON_NEWS_PATH}/output_1.json")

                    message1: str = SUMARIZATION_NEWS_CONTEXT.format(page_content=news1["Contenido"])
                    message2: str = SUMARIZATION_NEWS_CONTEXT.format(page_content=news2["Contenido"])

                    st.session_state.summarization1 = st.session_state.comparison_bot_1.chat(message1)
                    st.session_state.summarization2 = st.session_state.comparison_bot_2.chat(message2)
                
                else:
                    response1 = f"Error durante la comparación.\nPor favor, intenta de nuevo, o trata con otras fuentes."
                    response2 = f"Error durante la comparación.\nPor favor, intenta de nuevo, o trata con otras fuentes."
            
            except Exception as e:
                response1 = f"Error durante la comparación.\nPor favor, intenta de nuevo, o trata con otras fuentes."
                response2 = f"Error durante la comparación.\nPor favor, intenta de nuevo, o trata con otras fuentes."

                print("Error during comparison:", e)

        render_comparison_results(col1, col2, response1, response2)


def render_comparison_results(col1, col2, response1: str, response2: str):
    """
    Render the comparison results of the two news articles.
    """

    with col1:
            if not "summarization1" in st.session_state:
                st.markdown(f'<div class="comparison-bubble">{response1}</div>', unsafe_allow_html=True)

            else:
                st.markdown(f'<div class="comparison-bubble">{st.session_state.summarization1}</div>', unsafe_allow_html=True)
                
                if st.button("", key="btn_read_summary1", type="secondary", icon=":material/play_arrow:"):
                    speech_response(st.session_state.summarization1, st.session_state.text2speech_comparison)

    with col2:
        if not "summarization2" in st.session_state:
            st.markdown(f'<div class="comparison-bubble">{response2}</div>', unsafe_allow_html=True)

        else:
            st.markdown(f'<div class="comparison-bubble">{st.session_state.summarization2}</div>', unsafe_allow_html=True)
            
            if st.button("", key="btn_read_summary2", icon=":material/play_arrow:"):
                speech_response(st.session_state.summarization2, st.session_state.text2speech_comparison)


def start_comparison_side_bar():
    """
    Start the Streamlit sidebar for the comparison window.

    The sidebar contains the configuration options for the comparison chatbot in the comparison window.
    """
    
    if not "comparison_bot_1" in st.session_state or not "comparison_bot_2" in st.session_state:
        comparison_bot: Bot = Bot(
            st.session_state.api_key,
            st.session_state.selected_model,
            st.session_state.selected_provider,
            st.session_state.selected_language,
            st.session_state.temperature
        )

        st.session_state.comparison_bot_1 = comparison_bot
        st.session_state.comparison_bot_2 = comparison_bot

    if not "text2speech_comparison" in st.session_state:
        text2speech: TextToSpeech = TextToSpeech(
            st.session_state.google_api_key,
            st.session_state.selected_language,
            st.session_state.selected_voice,
            st.session_state.selected_voice_gender
        )

        st.session_state.text2speech_comparison = text2speech

    with st.sidebar:
        st.header("Configuración")

        st.write("<b>Noticias a comparar</b>", unsafe_allow_html=True)
        st.session_state.news1 = st.text_input("Noticias a comparar", label_visibility="collapsed", placeholder="Noticia 1", value="" if not "news1" in st.session_state else st.session_state.news1)
        st.session_state.news2 = st.text_input("Noticias a comparar 2", label_visibility="collapsed", placeholder="Noticia 2", value="" if not "news2" in st.session_state else st.session_state.news2)

        st.header("Configuración del Modelo")

        st.session_state.temperature_comparison = st.slider(
            label="Temperatura de Respuesta", 
            min_value=0.0, 
            max_value=2.0, 
            value=1.0
        )

        st.session_state.selected_model_comparison = AVAILABLE_MODELS.get(
            st.selectbox(
                "Modelo de lenguaje",
                AVAILABLE_MODELS.keys()
            )
        )

        st.session_state.selected_provider_comparison = LLM_PROVIDERS.get(st.session_state.selected_model_comparison)

        st.session_state.selected_language_comparison = AVAILABLE_LANGUAGES.get( 
            st.selectbox(
                "Lenaguaje",
                AVAILABLE_LANGUAGES.keys()
            )
        )

        st.header("Configuración de Voz")
        
        st.session_state.selected_voice_gender_comparison = AVAILABLE_VOICE_GENDERS.get(
            st.selectbox(
                "Género de Voz",
                AVAILABLE_VOICE_GENDERS
            )
        )
        
        voices: list[str] = AVAILABLE_VOICES.get(st.session_state.selected_voice_gender_comparison, [])
        voices = [voice for voice in voices if voice[:2] == st.session_state.selected_language_comparison.lower()]

        st.session_state.selected_voice_comparison = AVAILABLE_VOICES.get(
            st.selectbox(
                "Voz",
                voices
            )
        )

        if st.button("Recargar modelo"):
            reload_comparison_model()


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

    text2speech: TextToSpeech = TextToSpeech(
        st.session_state.google_api_key,
        st.session_state.selected_language,
        st.session_state.selected_voice,
        st.session_state.selected_voice_gender
    )

    st.session_state.bot = chatbot
    st.session_state.text2speech = text2speech


def reload_comparison_model():
    """
    Reload the comparison model with the latest configuration.
    """

    st.session_state.api_key = os.getenv("OPENAI_API_KEY") if st.session_state.selected_provider_comparison == "openai" else os.getenv("GROQ_API_KEY")

    text2speech: TextToSpeech = TextToSpeech(
        st.session_state.google_api_key,
        st.session_state.selected_language_comparison,
        st.session_state.selected_voice_comparison,
        st.session_state.selected_voice_gender_comparison
    )

    comparison_bot: Bot = Bot(
        st.session_state.api_key,
        st.session_state.selected_model_comparison,
        st.session_state.selected_provider_comparison,
        st.session_state.selected_language_comparison,
        st.session_state.temperature_comparison 
    )

    st.session_state.comparison_bot_1 = comparison_bot
    st.session_state.comparison_bot_2 = comparison_bot
    st.session_state.text2speech_comparison = text2speech


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


def load_json(file_path: str) -> dict:
    """
    Load a JSON file from the given file path.

    :param file_path: The path to the JSON file.
    :type file_path: str
    :return: The data from the JSON file.
    :rtype: dict
    """

    with open(file_path, "r", encoding="utf-8") as file:
        data: dict = json.load(file)

    return data


def speech_response(response: str, text2speech_instance: TextToSpeech):
    """
    Sends a speech response to the user.

    :param response: The text to be spoken.
    :type response: str
    """

    # st.session_state.text2speech.speech_response(response)
    text2speech_instance.speech_response(response)


start_ui()