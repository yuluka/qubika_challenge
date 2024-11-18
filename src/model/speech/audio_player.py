from pydub import AudioSegment
import time
import pyaudio
import threading


class AudioPlayer:
    """
    AudioPlayer class is a class that plays audio files. It is used by the TextToSpeech class to play the audio generated by the Google Cloud Text-to-Speech API.

    The main idea of this class is to play the audio in a separate thread, and to be able to pause, resume, and stop the audio.
    """

    def __init__(self, file_path):
        self.audio = AudioSegment.from_file(file_path)
        self.is_paused = False
        self.pause_time = 0
        self.stop_flag = False
        self.stream = None
        self.current_position = 0  # To keep track of the current position in the audio

        self.playing = False

        self.p = pyaudio.PyAudio()

    def play(self):
        """
        Plays the audio file.
        """

        self.beg_time = time.time()

        self.playing = True
        self.is_paused = False
        self.stop_flag = False
        # self._play_from(self.pause_time)
        threading.Thread(target=self._play_from, args=(self.pause_time,)).start()

    def _play_from(self, start_time):
        """
        Plays the audio file from a specific start time.

        :param start_time: The start time in milliseconds.
        """

        audio_segment = self.audio[start_time:]
        raw_data = audio_segment.raw_data
        sample_width = audio_segment.sample_width
        frame_rate = audio_segment.frame_rate
        channels = audio_segment.channels
        total_frames = len(raw_data) // (sample_width * channels)
        self.current_position = 0

        def callback(in_data, frame_count, time_info, status):
            """
            Callback function for the audio stream.
            """

            if self.is_paused or self.stop_flag:
                return (None, pyaudio.paComplete)

            end_position = self.current_position + frame_count * sample_width * channels
            data = raw_data[self.current_position : end_position]
            self.current_position += len(data)

            return (
                data,
                (
                    pyaudio.paContinue
                    if len(data) == frame_count * sample_width * channels
                    else pyaudio.paComplete
                ),
            )

        self.stream = self.p.open(
            format=self.p.get_format_from_width(sample_width),
            channels=channels,
            rate=frame_rate,
            output=True,
            stream_callback=callback,
        )

        self.stream.start_stream()

        while self.stream.is_active():
            if self.is_paused:
                break

            if self.stop_flag:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
                break

            time.sleep(0.1)

        # Calculate the pause time to be able to resume the audio from the correct position
        self.end_time = time.time()
        self.pause_time += (self.end_time - self.beg_time) * 1000

    def pause(self):
        """
        Pauses the audio.
        """

        if self.stream and self.stream.is_active():
            print("PAUSING")
            self.is_paused = True
            self.stream.stop_stream()

    def resume(self):
        """
        Resumes the audio.
        """

        if self.is_paused:
            print("RESUMING")
            self.is_paused = False

            self.beg_time = time.time()
            self.play()

    def stop(self):
        """
        Stops the audio.
        """

        self.stop_flag = True

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

        self.is_paused = False
        self.pause_time = 0
        self.current_position = 0
        self.playing = False

    def is_playing(self):
        """
        Checks if the audio is playing.
        """

        # The reason to do this check in this way is because it is always a little bit of difference between the duration of the audio and the calculated pause time.
        if (self.audio.duration_seconds * 1000 - self.pause_time) < 1000:
            self.playing = False

        return self.playing

    def __del__(self):
        """
        Destructor.
        """

        if self.stream:
            self.stream.close()

        self.p.terminate()