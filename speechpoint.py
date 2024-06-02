import speech_recognition as sr
from loguru import logger
#从系统麦克风拾取音频数据，采样率为 16000
def record():
    rate=16000
    r = sr.Recognizer()
    with sr.Microphone(sample_rate=rate) as source:
        r.adjust_for_ambient_noise(source)
        #os.system('aplay ding.wav')
        #snowboydecoder.play_audio_file()
        #time.sleep(1)
        logger.info('正在获取声音中...')
        audio = r.listen(source)
    # with sr.AudioFile
        # print(r.recognize_google(audio, language='zh-CN'))
        # a = audio.get_wav_data()
#    with open("question.w", "wb") as f:
#        f.write(audio.get_wav_data())
        logger.info('声音获取完成.')
    return audio
def record_file():

    rate=16000
    r = sr.Recognizer()
    with sr.Microphone(sample_rate=rate) as source:

        #r.adjust_for_ambient_noise(source)
        #os.system('aplay ding.wav')
        #time.sleep(1)
        logger.info('正在获取声音中...')
        audio = r.listen(source,6,6)

    # with sr.AudioFile
        # print(r.recognize_google(audio, language='zh-CN'))
        # a = audio.get_wav_data()
    with open("Sound/question.wav", "wb") as f:
        f.write(audio.get_wav_data())
        logger.info('声音获取完成.')
        f.close()

#record()
