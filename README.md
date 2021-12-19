# opencv_video_with_audio
opencv video with audio play

## usage

```sh
usage: video_with_audio.py [-h] --video VIDEO --audio AUDIO [--use-pyaudio USE_PYAUDIO]

optional arguments:
  -h, --help            show this help message and exit
  --video VIDEO
  --audio AUDIO         `.wav` file.
                        `.wav` file can be retrieved from video stream by:
                        ffmpeg -i my_video.mp4 -vn -f wav my_audio.wav
  --use-pyaudio USE_PYAUDIO
                        Use pyadio or ffpyplayer. default pyaudio.
                        If this option is set as false, the same file can be specified for video and audio.
```
