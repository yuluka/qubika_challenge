from google.cloud import texttospeech

from pydub import AudioSegment
from pydub.playback import play
import os

from model.speech.audio_player import AudioPlayer


class TextToSpeech:
    """
    TextToSpeech class is a class that converts text to speech using the Google Cloud Text-to-Speech API.
    """

    def __init__(self, google_api_key: str, language: str, voice: str, gender: str):
        self.base_path: str = os.path.dirname(os.path.abspath(__file__))
        self.base_path = os.path.dirname(self.base_path)
        self.base_path = os.path.dirname(self.base_path)

        self.LANGUAGE: str = language
        self.VOICE: str = voice
        self.GOOGLE_API_KEY: str = google_api_key
        self.GENDER: str = gender
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.GOOGLE_API_KEY

        self.player = None

    def speech_response(self, text):
        """
        Generates a speech response from a given text and plays it.

        :param text: The text to be converted to speech.
        """

        speech_name = self.generate_speech(text)

        self.player = AudioPlayer(speech_name)
        self.player.play()

    def generate_speech(self, text):
        """
        Generates a speech response from a given text, using the Google Cloud Text-to-Speech API.

        :param text: The text to be converted to speech.
        :return: The name of the file with the speech.
        """

        client = texttospeech.TextToSpeechClient()

        synthesis_input = texttospeech.SynthesisInput(text=text)

        language_code = "es-US" if self.LANGUAGE == "ES" else "en-US"
        ssml_gender = texttospeech.SsmlVoiceGender.MALE if self.GENDER == "male" else texttospeech.SsmlVoiceGender.FEMALE

        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            # name="es-US-Neural2-C" if self.LANGUAGE == "ES" else "en-US-Neural2-J",
            name=self.VOICE,
            ssml_gender=ssml_gender,
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = client.synthesize_speech(
            request={
                "input": synthesis_input,
                "voice": voice,
                "audio_config": audio_config,
            }
        )

        speech_name = os.path.join(
            self.base_path, "model", "speech", "response_speech.mp3"
        )

        with open(speech_name, "wb") as out:
            out.write(response.audio_content)

        return speech_name

    def pause(self):
        """
        Pauses the speech.
        """

        if self.player:
            self.player.pause()

    def resume(self):
        """
        Resumes the speech.
        """

        if self.player:
            self.player.resume()

    def stop(self):
        """
        Stops the speech.
        """

        if self.player:
            self.player.stop()
