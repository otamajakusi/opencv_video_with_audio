class AudioDataMixin:
    def process_audio(self, data, width, channels, framerate):
        print(f"{width=},{channels=},{framerate=}")
