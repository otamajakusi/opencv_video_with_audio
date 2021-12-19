import cv2
import time

# for WithPyAudio
import pyaudio
import wave

# for WithMediaPlayer
from ffpyplayer.player import MediaPlayer


class WithPyAudio:
    # https://people.csail.mit.edu/hubert/pyaudio/docs/#example-callback-mode-audio-i-o

    def __init__(self, audio_file):
        wf = wave.open(audio_file, "rb")
        p = pyaudio.PyAudio()
        stream = p.open(
            format=p.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True,
            stream_callback=self._stream_cb,
        )
        self.wf = wf
        self.p = p
        self.stream = stream

    def get_frame(self):
        if not self.stream.is_active():
            return False
        return True

    def close(self):
        self.stream.stop_stream()
        self.stream.close
        self.p.terminate()
        self.wf.close()

    def _stream_cb(self, in_data, frame_count, time_info, status):
        data = self.wf.readframes(frame_count)
        return (data, pyaudio.paContinue)


class WithMediaPlayer:
    def __init__(self, audio_file):
        self.player = MediaPlayer(audio_file)

    def get_frame(self):
        _, val = self.player.get_frame(show=False)
        if val == "eof":
            return False
        return True

    def close(self):
        if self.player:
            self.player.close_player()
            self.player = None


def main(video_file, audio_file):
    cap = cv2.VideoCapture(video_file)

    # player = WithMediaPlayer(audio_file)
    player = WithPyAudio(audio_file)
    start_time = time.time()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if not player.get_frame():
            break

        cv2.imshow(video_file, frame)

        elapsed = (time.time() - start_time) * 1000  # msec
        play_time = int(cap.get(cv2.CAP_PROP_POS_MSEC))
        sleep = max(1, int(play_time - elapsed))
        if cv2.waitKey(sleep) & 0xFF == ord("q"):
            break

    player.close()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--audio")
    args = parser.parse_args()
    main(args.video, args.audio if args.audio else args.video)
