from groq import Groq
from openai import OpenAI
import os

class Bot:
    """
    Class Bot is a class that represents a chatbot. It is responsible for handling the conversation with the user and sending messages to the model.

    The Bot class is used to interact with the OpenAI or Llama3 models.
    """

    def __init__(self, api_key: str, model: str, provider: str, language: str, temperature: float):
        self.API_KEY = api_key
        self.MODEL = model
        self.PROVIDER = provider
        self.LANGUAGE = language
        self.TEMPERATURE = temperature

        self.init_config()

    def init_config(self):
        """
        Initializes the configuration of the bot.

        Stablishes the context of the conversation and initializes the OpenAI or Llama3 client, depending on the model selected by the user.
        """

        if self.LANGUAGE == "EN":
            context = "You are a virtual assistant. You must speak english. Your manner must be cordial."
        elif self.LANGUAGE == "ES":
            context = "Eres un asistente virtual. Debes hablar en español. Tu trato debe ser cordial."

        self.message_history = [{"role": "system", "content": context}]

        if self.PROVIDER == "openai":
            self.init_openai()
        elif self.PROVIDER == "groq":
            self.init_groq()

    def init_openai(self):
        """
        Initializes the OpenAI client.
        """

        self.client = OpenAI(
            api_key=self.API_KEY,
        )

    def init_groq(self):
        """
        Initializes the Llama3 client.
        """

        self.client = Groq(
            api_key=self.API_KEY,
        )

    def chat(self, message: str) -> str:
        """
        Sends a message to the model and returns the response.

        :param message: The message history to send to the model.
        :type message_history: list[dict[str, str]]
        :return: The response from the model.
        :rtype: str
        """

        if self.PROVIDER == "openai":
            return self.chat_openai(message)
        elif self.PROVIDER == "groq":
            return self.chat_groq(message)

    def chat_openai(self, message: str) -> str:
        """
        Sends a message to the OpenAI model and returns the response.

        :param message: The message to send to the model.
        :type message: str
        :return: The response from the model.
        :rtype: str
        """

        self.message_history.append({"role": "user", "content": message})

        completion = self.client.chat.completions.create(
            model=self.MODEL,
            messages=self.message_history,
            temperature=self.TEMPERATURE,
        )

        response = completion.choices[0].message.content or ""

        self.message_history.append({"role": "assistant", "content": response})

        return response

    def chat_groq(self, message: str) -> str:
        """
        Sends a message to a model hosted by Groq and returns the response.

        :param message: The message to send to the model.
        :type message: str
        :return: The response from the model.
        :rtype: str
        """

        self.message_history.append({"role": "user", "content": message})

        completion = self.client.chat.completions.create(
            model=self.MODEL,
            messages=self.message_history,
            temperature=self.TEMPERATURE,
            max_tokens=8192,
            top_p=1,
            stream=True,
            stop=None,
        )

        response = ""

        for chunk in completion:
            response += chunk.choices[0].delta.content or ""

        self.message_history.append({"role": "assistant", "content": response})

        return response