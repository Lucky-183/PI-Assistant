
import time
import pymysql
import tts
from threading import Thread
import time
import cn2an
from play import play
from loguru import logger
flag = False
flag2 = False
nextime=None

def if_schedule(text):
    global flag, flag2
    try:
        content = ''
        for i in [',',':','.','、','，','。',' ']:
            text = text.replace(i, '')
        if '的闹钟' in text and '一个' in text:
            if '提醒我' in text:
                content = text.split('提醒我')[1]
                logger.info(content)
            text = text[text.find('一个') + 2:text.find('的闹钟')]
            day = time.strftime('%d', time.localtime())
            hour_now = time.strftime('%H', time.localtime())
            if '天' in text:
                timearray = text.split('天')
                if timearray[0] == '明' and int(hour_now) > 3:
                    day = str(int(day) + 1)
                elif timearray[0] == '后':
                    day = str(int(day) + 2)
                text = text[text.find('天') + 1:]
                flag = True
            if '上午' in text or '早上' in text:
                text = text[2:]
            elif '下午' in text or '晚上' in text:
                text = text[2:]
                flag2 = True
            timearray = text.split('点')
            timearray[0] = cn2an.cn2an(timearray[0], 'smart')
            timearray[1] = cn2an.transform(timearray[1], 'cn2an')
            if timearray[1] == '':
                minute = '00'
            elif timearray[1] == '0.5':
                minute = '30'
            elif '分' in timearray[1]:
                timearray[1]=timearray[1][:timearray[1].find('分')]
                minute = timearray[1]
            else:
                minute = timearray[1]
            if flag2 is True:
                flag2 = False
                timearray[0] = str(int(timearray[0]) + 12)
            if flag is False:
                if int(timearray[0]) < int(hour_now):
                    hour = str(int(timearray[0]) + 12)
                    if int(hour) < int(hour_now):
                        hour = str(int(timearray[0]))
                        day = str(int(day) + 1)
                    elif int(hour) == int(hour_now):
                        minute_now = time.strftime('%M', time.localtime())
                        if int(minute) < int(minute_now):
                            hour = str(int(timearray[0]))
                            day = str(int(day) + 1)
                        else:
                            hour = str(int(timearray[0])+12)
                else:
                    hour = str(int(timearray[0]))
            else:
                flag = False
                hour = str(int(timearray[0]))
            if int(hour) >= 24:
                hour = str(int(hour) - 24)
                day = str(int(day) + 1)
            Time = time.strftime('%Y-%m-', time.localtime()) + f'{day} {hour}:{minute}:00'
            # date_time_str = cn2an.transform(date_time_str,'cn2an')
            logger.info(Time)
            logger.info(f'已为您设定好{day}日{hour}:{minute}的闹钟,{("事项为"+content) if content != "" else ""}')
            make(Time,content)
            tts.ssml_save(f'已为您设定好{day}日{hour}点{minute}分的闹钟,{("事项为"+content) if content != "" else ""}','Sound/schedulenotify.raw')
            play('Sound/ding.wav')
            play('Sound/schedulenotify.raw')
            return True

        for i in ["后提醒我", "后叫我"]:
            if i in text:
                text = cn2an.transform(text, 'cn2an')
                hour = 0
                minute = 0
                sec = 0
                strr = text.split(i)
                content = strr[1]
                strr = strr[0]
                logger.info(content)
                if '小时' in strr:
                    hour = int(strr[:strr.find('小时')])
                    strr = strr[strr.find('小时') + 2:]

                if '分' in strr:
                    minute = int(strr[:strr.find('分')])
                    if '分钟' in strr:
                        strr = strr[strr.find('分钟') + 2:]
                    else:
                        strr = strr[strr.find('分') + 1:]

                if '秒' in strr:
                    sec = int(strr[:strr.find('秒')])
                t = hour * 60 * 60 + minute * 60 + sec
                Time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time()) + t))

                logger.info(Time)
                logger.info(f'将在{time.strftime("%H:%M",time.localtime(int(time.time()) + t))}时提醒你,{("事项为"+content) if content != "" else ""}')
                make(Time, content)
                tts.ssml_save(f'将在{time.strftime("%H:%M",time.localtime(int(time.time()) + t))}时提醒你,{("事项为"+content) if content != "" else ""}', 'Sound/schedulenotify.raw')
                play('Sound/ding.wav')
                play('Sound/schedulenotify.raw')
                return True

        for i in ["时提醒我", "时叫我", "提醒我", "叫我"]:
            if i in text:
                strr = text.split(i)
                content = strr[1]
                timerr = strr[0]
                hour_now = time.strftime('%H', time.localtime())
                if '上午' in timerr:
                    timerr = timerr[2:]
                elif '下午' in timerr or '晚上' in timerr:
                    timerr = timerr[2:]
                    flag2 = True
                timearray = timerr.split('点')
                timearray[0] = cn2an.cn2an(timearray[0], 'smart')
                timearray[1] = cn2an.transform(timearray[1], 'cn2an')
                if timearray[1] == '':
                    minute = '00'
                elif timearray[1] == '0.5':
                    minute = '30'
                elif '分' in timearray[1]:
                    timearray[1] = timearray[1][:timearray[1].find('分')]
                    minute = timearray[1]
                else:
                    minute = timearray[1]
                if flag2 is True:
                    flag2 = False
                    timearray[0] = str(int(timearray[0]) + 12)
                if flag is False:
                    if int(timearray[0]) < int(hour_now):
                        hour = str(int(timearray[0]) + 12)
                        if int(hour) < int(hour_now):
                            hour = str(int(timearray[0]))
                    else:
                        hour = str(int(timearray[0]))
                else:
                    flag = False
                    hour = str(int(timearray[0]))
                Time = time.strftime('%Y-%m-%d', time.localtime()) + f' {hour}:{minute}:00'

                logger.info(Time)
                logger.info(f'将在{hour}点{minute}分时提醒你,{("事项为" + content) if content != "" else ""}')
                make(Time, content)
                tts.ssml_save(f'将在{hour}点{minute}分时提醒你,{("事项为" + content) if content != "" else ""}',
                              'Sound/schedulenotify.raw')
                play('Sound/ding.wav')
                play('Sound/schedulenotify.raw')
                return True

        for i in ["计时", "倒计时"]:
            if i in text:
                text = cn2an.transform(text, 'cn2an')
                hour = 0
                minute = 0
                sec = 0
                strr = text.split(i)
                strr = strr[1]
                if '小时' in strr:
                    hour = int(strr[:strr.find('小时')])
                    strr = strr[strr.find('小时') + 2:]

                if '分' in strr:
                    minute = int(strr[:strr.find('分')])
                    if '分钟' in strr:
                        strr = strr[strr.find('分钟') + 2:]
                    else:
                        strr = strr[strr.find('分') + 1:]

                if '秒' in strr:
                    sec = int(strr[:strr.find('秒')])

                t = hour * 60 * 60 + minute * 60 + sec
                Time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time()) + t))

                logger.info(Time)
                logger.info(f'将在{time.strftime("%H:%M",time.localtime(int(time.time()) + t))}时提醒你')
                make(Time)
                tts.ssml_save(f'将在{time.strftime("%H:%M",time.localtime(int(time.time()) + t))}时提醒你',
                              'Sound/schedulenotify.raw')
                play('Sound/ding.wav')
                play('Sound/schedulenotify.raw')
                return True
    except Exception as e:
        logger.warning(e)
        play('Sound/failclock.raw')

    return False


def sql_add(time,content):
    db = pymysql.connect(host="127.0.0.1", user="root", password="123456", database="schedule")

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # 执行完毕后返回的结果默认以元组显示
    # 使用execute方法执行SQL语句
    sql=f"insert into main (time,content) values ({time},'{content}')"
    try:
         # 执行sql语句
        cursor.execute(sql)
        db.commit()
         # 执行sql语句
    except Exception as e:
         logger.warning(e)
    # 关闭数据库连接
    db.close()

def sql_del(cls,thing):

    db = pymysql.connect(host="127.0.0.1", user="root", password="123456", database="schedule")

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # 执行完毕后返回的结果默认以元组显示
    # 使用execute方法执行SQL语句
    if cls == 'id':
        sql=f"delete from main where id = {thing}"
    elif cls == 'time':
        sql = f"delete from main where time = {thing}"
    else:
        return
    try:
        cursor.execute(sql)
        db.commit()
         # 执行sql语句
    except Exception as e:
         logger.warning(e)
    db.close()

def sql_getlist(index):

    db = pymysql.connect(host="127.0.0.1", user="root", password="123456", database="schedule")

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # 执行完毕后返回的结果默认以元组显示
    # 使用execute方法执行SQL语句
    # sql="insert into main values (1837699517,0)"
    sql=f"select {index} from main order by time"
    try:
         # 执行sql语句
         cursor.execute(sql)
         list=cursor.fetchall()
         # 执行sql语句
    except Exception as e:
          logger.warning(e)
    db.close()
    return list

# sql_add(int(time.time()),'你好')



def make(Time, content=''):

    try:
        timestamp = time.mktime(time.strptime(Time, "%Y-%m-%d %H:%M:%S"))
        sql_add(int(timestamp), content)
        alter()
        return [Time,content]
    except Exception as e:
        logger.warning(e)
        play('Sound/failclock_format.raw')
# make('2023-8-12 12:34:12','')

def cancel(cls,thing):
    sql_del(cls,thing)
    alter()

    logger.info(f'{thing} canceling')


def alter():
    global nextime
    if len(sql_getlist('time')):
        for i in sql_getlist('time'):
            if i[0] > int(time.time()):
                nextime=i[0]
                logger.info(f'nexttime:{nextime}')
                break
    else:
        nextime=None

def time_up():
    global nextime
    nextime=None
    alter()

    logger.info(f'您设定的时间到了,{"" if sql_getlist("*")[0][2] == "" else ("晓晓提醒您:"+sql_getlist("*")[0][2])}')
    tts.ssml_save(f'您设定的时间到了,{"" if sql_getlist("*")[0][2] == "" else ("晓晓提醒您:"+sql_getlist("*")[0][2])}','Sound/schedulenotify.raw')

    play('Sound/ding.wav')
    play('Sound/ding.wav')
    play('Sound/schedulenotify.raw')


    for i in sql_getlist('time'):
        if i[0] < int(time.time()):
            cancel('time', i[0])


def timer():
    for i in sql_getlist('time'):
        if i[0] < int(time.time()):
            cancel('time', i[0])
            logger.info(f'{i[0]},has been cancel')

    global nextime
    while(1):
        if nextime:
            if int(time.time())>=nextime:
                time_up()
        time.sleep(1)


if __name__ == "__main__":
    make('2023-8-4 23:45:44','12')


