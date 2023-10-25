from play import play
def ifend(text):
    if text == "" or text.find('结束对话') != -1 or text.find('没事了') != -1 or text.find('没事儿了') != -1 or text.find('退一下吧') != -1 or text.find('退下吧') != -1 or text.find('退一下')!=-1 or text.find('退下')!=-1 or text=='闭嘴。' or text=='查。':
        play('Sound/ding.wav')
        play('Sound/quit.wav')
        return True
    return False

def ifexit(text):
    if text.find('程序') != -1 and( text.find('结束') != -1 or  text.find('终止') != -1 or text.find('退出') != -1 ):
        play('Sound/exit.wav')
        return True
    return False
