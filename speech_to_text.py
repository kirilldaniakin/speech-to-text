import sys
import os
import json
import wave
import requests
import zipfile
import io
import numpy as np
import soundfile as sf
from librosa.effects import time_stretch
from typing import List, Dict
from vosk import Model, KaldiRecognizer, SetLogLevel


def modify_audio(audio: np.ndarray, rate: float, volume_factor: float) -> np.ndarray:
    """
    changes an input audio's sample_rate and volume without affecting the pitch.
    
    :param audio: input audio array.
    :param rate: new sample rate.
    :param volume_factor: coefficient of volume increase or decrease.
    :returns: modified audio array.
    """
    return time_stretch(audio, rate=rate) * volume_factor


def _speech_recognition(model_on_disk: str, wav: wave.Wave_read) -> Dict:
    # initialize the model and speech recognizer
    model = Model(model_on_disk)
    rec = KaldiRecognizer(model, wav.getframerate())

    # read the audio and transform a speech in it to text
    while True:
        data = wav.readframes(4000)
        if len(data) == 0:
            break
        if not rec.AcceptWaveform(data):
            print(json.loads(rec.PartialResult()))

    return json.loads(rec.FinalResult())


def speech_to_text(wav: wave.Wave_read, models_on_disk: List[str]) -> Dict:
    """
    translates speech in audio wav to text in English and Russian.

    :param wav: input Wave_read pointing to the beginning of an audio file.
    :param models_on_disk: vosk models to use for speech recognition.
    :returns: STT transcribtion for each model from models_on_disk
    """

    out_dict = {}
    for model_on_disk in models_on_disk:
        recognized = _speech_recognition(model_on_disk, wav)
        out_dict[model_on_disk] = recognized["text"]
        # move the pointer back to the beginning of the audio file
        wav.rewind()

    return out_dict


if __name__ == "__main__":
    SetLogLevel(0)
    if len(sys.argv) < 4:
        print(f"Modifies and transcribes a wave file.\n\n" +\
            f"Usage: {sys.argv[0]} sample_rate_factor volume_factor path_to_input_filename.wav path_to_output_filename.wav")
        sys.exit(-1)
    try:
        new_rate = float(sys.argv[1])
        volume_factor = float(sys.argv[2])
        if new_rate <= 0 or volume_factor <= 0:
            raise Exception
    except:
        print('sample_rate_factor and volume_factor must be positive numbers')
        sys.exit(-1)
    
    wav = wave.open(sys.argv[3], "rb")
    if wav.getnchannels() != 1 or wav.getsampwidth() != 2 or wav.getcomptype() != "NONE":
        print("Audio file must be WAV format mono PCM.")
        sys.exit(1)
    frames = wav.readframes(wav.getnframes())
    audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32)
    scale = 1. / float(1 << ((8 * wav.getsampwidth()) - 1)) # from librosa
    audio *= scale
    
    sample_rate = wav.getframerate()

    # since we read frames, we need to move the pointer back to the beginning of the file
    wav.rewind()

    # modify the audio and save it on disk under specified path
    new_audio = modify_audio(audio, new_rate, volume_factor)

    try:
        sf.write(sys.argv[4], new_audio, sample_rate)
        print(f"Modified audio saved at {sys.argv[4]}")
    except Exception as ex:
        print("Something went wrong with saving a modified file")
        print(Exception)  

    models_on_disk = ['vosk-model-small-en-us-0.15', 'vosk-model-small-ru-0.22']

    urls_to_models = ["https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
                        "https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip"]
    
    models_urls_dict = dict(zip(models_on_disk, urls_to_models))

    
    for dir, url in models_urls_dict.items():
        if not os.path.isdir(dir):
            print(f"Downloading {dir}")
            # download and extract models for speech to text
            r = requests.get(url)
            z = zipfile.ZipFile(io.BytesIO(r.content))
            z.extractall("")

    stt_result = speech_to_text(wav, models_on_disk)

    with open('STT_result.json', 'w') as fp:
        json.dump(stt_result, fp)
    print("The speech-to-text results is saved to STT_result.json")
    # to make sure json was saved correctly:
    # with open('STT_result.json') as json_file:
    #     data = json.load(json_file)
 
    # # Print the type of data variable
    # print("Type:", type(data))
    # print("Data:", data)
    











