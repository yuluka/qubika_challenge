from groq import Groq

import streamlit as st


AVAILABLE_MODELS: dict[str, str] = {
    "GPT 4o": "gpt-4o",
    "GPT 3.5": "gpt-3.5 turbo",
    "Llama 3.1 - 70b" : "llama3-70b-8192",
    "Llama 3.1 - 70b" : "llama3-70b-8192",
    "Llama 3.2 - 3b" : "llama-3.2-3b-preview",
    "Llama 3.2 - 90b" : "llama-3.2-90b-text-preview",
    "Gemma - 7b" : "gemma-7b-it",
    "Gemma 2 - 9b" : "gemma2-9b-it",
}


temperature: float = 1.0
selected_model: str = ""


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

        st.session_state.messages.append({"role": "user", "content": prompt})

        # response = chat_groq(st.session_state.messages)
        response = f"Echo: {prompt}"

        with st.chat_message("assistant"):
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})


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

        print(selected_model)


start_ui()