# speech-to-text
Simple python console application for modifying a wav audio speed and volume and translating speech in it into text offline.  
Input audio file must be WAV format mono PCM.

Usage: python speech_to_text.py rate_factor volume_factor path_to/audio_in.wav path_to/audio_out.wav

The audio with modified speed and volume will be saved to path_to/audio_out.wav  

rate_factor and volume_factor control how much faster (or slower, given rate_factor < 1) and louder (or quieter, given volume_factor < 1) the output audio will be as compared to input.

For offline speech-to-text the [vosk](https://github.com/alphacep/vosk-api) library was used with small Russian and English models downloaded from [the vosk website](https://alphacephei.com/vosk/models). For simplicity, the speech language is not identified (I experimented with [AttRnn7lang](https://github.com/zkmkarlsruhe/language-identification), however the result was not satisfactory), but the app saves a transcription for all of the used models for potential postprocessing and later use. The result of the speech-to-text is saved to a json file in the same directory the app was launched from.

  

