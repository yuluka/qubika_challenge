from groq import Groq
from openai import OpenAI
import os

class Bot:
    """
    Class Bot is a class that represents a chatbot. It is responsible for handling the conversation with the user and sending messages to the model.

    The Bot class is used to interact with the OpenAI or Llama3 models.
    """

    def __init__(self, api_key: str, model: str, language: str):
        self.API_KEY = api_key
        self.MODEL = model
        self.LANGUAGE = language

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

        if self.MODEL == "gpt-3.5-turbo" or self.MODEL == "gpt-4o":
            self.init_openai()
        elif self.MODEL == "llama3-70b-8192":
            self.init_groq_llama3()

    def init_openai(self):
        """
        Initializes the OpenAI client.
        """

        self.client = OpenAI(
            api_key=self.API_KEY,
        )

    def init_groq_llama3(self):
        """
        Initializes the Llama3 client.
        """

        self.client = Groq(
            api_key=self.API_KEY,
        )


    def chat(self, message_history: list[dict[str, str]]) -> str:
        """
        Sends a message to the model and returns the response.

        :param message: The message history to send to the model.
        :type message_history: list[dict[str, str]]
        :return: The response from the model.
        :rtype: str
        """

        if self.MODEL == "gpt-3.5-turbo" or self.MODEL == "gpt-4o":
            return self.chat_openai(message_history)
        elif(self.MODEL == "llama3-70b-8192"):
            return self.chat_groq(message_history)

    def chat_openai(self, message: str) -> str:
        """
        Sends a message to the OpenAI model and returns the response.

        :param message: The message to send to the model.
        :type message: str
        :return: The response from the model.
        :rtype: str
        """

        completion = self.client.chat.completions.create(
            model=self.MODEL,
            messages=self.message_history,
            temperature=1,
        )

        response = completion.choices[0].message.content or ""

        return response


    def chat_groq(self, message_history: list[dict[str, str]]) -> str:
        """
        Sends a message to the llama3 model and returns the response.

        :param message: The message to send to the model.
        :type message: str
        :return: The response from the model.
        :rtype: str
        """

        completion = self.client.chat.completions.create(
            model="llama3-70b-8192",
            messages=message_history,
            temperature=1,
            max_tokens=8192,
            top_p=1,
            stream=True,
            stop=None,
        )

        response = ""

        for chunk in completion:
            response += chunk.choices[0].delta.content or ""

        return response