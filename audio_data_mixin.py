import numpy as np

import torch
import torchaudio
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

from vad import VAD

model_name = "container_0/wav2vec2-large-xlsr-ja"
device = "cuda"
processor_name = "container_0/wav2vec2-large-xlsr-ja"

model = Wav2Vec2ForCTC.from_pretrained(model_name).to(device)
processor = Wav2Vec2Processor.from_pretrained(processor_name)


class AudioDataMixin:
    WIDTH_DICT = {1: np.int8, 2: np.int16, 3: np.int32}
    vad = VAD(0.8)

    tmp = []
    speech = []

    def process_audio(self, data, width, channels, framerate):
        # print(f"{width=},{channels=},{framerate=}")
        assert channels <= 2, f"{channel=}"
        """
        if channels == 2:
            ndata = ndata[::2] // 2 + ndata[1::2] // 2
        print(ndata.shape)
        resampler = torchaudio.transforms.Resample(orig_freq=framerate, new_freq=16_000)
        tdata = resampler.forward(torch.from_numpy(self._int2float(ndata)))
        """
        if len(self.tmp) > 3:
            data = b"".join(self.tmp)
            self.tmp = []
        else:
            self.tmp.append(data)
            return
        ndata = np.frombuffer(data, np.int16)
        fdata = self.vad._int2float(ndata)
        tdata = torch.from_numpy(fdata)

        vad_outs = self.vad._validate(tdata)
        confidence = vad_outs[:, 1].numpy()[0].item()
        if confidence > self.vad.confidence:
            # print(f"speeking {confidence:.2f}")
            self.speech.append(data)
        else:
            if len(self.speech):
                ndata = np.frombuffer(b"".join(self.speech), self.WIDTH_DICT[width])
                fdata = self.vad._int2float(ndata)
                out = self.predict(fdata, 16_000)
                if len(out[0]):
                    print(out)

                self.speech = []

    def predict(self, data, sampling_rate):
        features = processor(
            data,
            sampling_rate=sampling_rate,
            padding=True,
            return_tensors="pt",
        )
        input_values = features.input_values.to(device)
        attention_mask = features.attention_mask.to(device)
        with torch.no_grad():
            logits = model(input_values, attention_mask=attention_mask).logits

        decoded_results = []
        for logit in logits:
            pred_ids = torch.argmax(logit, dim=-1)
            decoded_results.append(processor.decode(pred_ids))
        return decoded_results
