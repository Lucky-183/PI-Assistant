#!/usr/bin/env python3

import wave
import sys
import json
from vosk import Model, KaldiRecognizer, SetLogLevel

# You can set log level to -1 to disable debug messages
SetLogLevel(-1)
#
#wf = wave.open(sys.argv[1], "rb")
#if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
#    print("Audio file must be WAV format mono PCM.")
#    sys.exit(1)

#model = Model("/home/pi/xiaoxiao/voskReco/model")

model = Model("voskReco/model")

def recognize(file='Sound/question.wav'):
    rec = KaldiRecognizer(model, 16000)
    with wave.open(file,'rb') as wf:
        rec.AcceptWaveform(wf.readframes(wf.getnframes())); 

    return json.loads(rec.FinalResult())["text"].replace(" ","")

if __name__=='__main__':
    words=recognize(sys.argv[1])
    print(words)
