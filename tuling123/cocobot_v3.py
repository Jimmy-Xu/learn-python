# -*- coding: utf-8 -*-
import urllib
import json
import fire

from aip import AipSpeech  # 百度语音合成
import subprocess  # 调用命令行 afplay
import os
import config

from pyaudio import PyAudio, paInt16
import numpy as np
from datetime import datetime
import wave


def getHtml(url):
    page = urllib.urlopen(url)
    html = page.read()
    return html

# 录音
class Recoder:
    NUM_SAMPLES = 2000  # pyaudio内置缓冲大小
    SAMPLING_RATE = 8000  # 取样频率
    LEVEL = 500  # 声音保存的阈值
    COUNT_NUM = 20  # NUM_SAMPLES个取样之内出现COUNT_NUM个大于LEVEL的取样则记录声音
    SAVE_LENGTH = 8  # 声音记录的最小长度：SAVE_LENGTH * NUM_SAMPLES 个取样
    TIME_COUNT = 60  # 录音时间，单位s

    Voice_String = []

    def savewav(self, filename):
        wf = wave.open(filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(self.SAMPLING_RATE)
        wf.writeframes(np.array(self.Voice_String).tostring())
        # wf.writeframes(self.Voice_String.decode())
        wf.close()

    def recoder(self):
        pa = PyAudio()
        stream = pa.open(format=paInt16, channels=1, rate=self.SAMPLING_RATE, input=True,
                         frames_per_buffer=self.NUM_SAMPLES)
        save_count = 0
        save_buffer = []
        time_count = self.TIME_COUNT

        while True:
            time_count -= 1
            # print time_count
            # 读入NUM_SAMPLES个取样
            string_audio_data = stream.read(self.NUM_SAMPLES)
            # 将读入的数据转换为数组
            audio_data = np.fromstring(string_audio_data, dtype=np.short)
            # 计算大于LEVEL的取样的个数
            large_sample_count = np.sum(audio_data > self.LEVEL)
            
            #print(np.max(audio_data))
            
            # 如果个数大于COUNT_NUM，则至少保存SAVE_LENGTH个块
            if large_sample_count > self.COUNT_NUM:
                save_count = self.SAVE_LENGTH
            else:
                save_count -= 1

            if save_count < 0:
                save_count = 0

            if save_count > 0:
                # 将要保存的数据存放到save_buffer中
                #print  save_count > 0 and time_count >0
                save_buffer.append(string_audio_data)
            else:
                #print save_buffer
                # 将save_buffer中的数据写入WAV文件，WAV文件的文件名是保存的时刻
                #print "debug"
                if len(save_buffer) > 0:
                    self.Voice_String = save_buffer
                    save_buffer = []
                    print("Recode a piece of  voice successfully!")
                    return True
            if time_count == 0:
                if len(save_buffer) > 0:
                    self.Voice_String = save_buffer
                    save_buffer = []
                    print("Recode a piece of  voice successfully!")
                    return True
                else:
                    return False


class CocoBot(object):
    """A simple bot class."""

    def __init__(self):
        self.client = AipSpeech(
            config.APP_ID, config.API_KEY, config.SECRET_KEY)
        self.rec = Recoder()

    # 语音合成
    def speak(self, sentence):
        result = self.client.synthesis(sentence, 'zh', 1, {'vol': 5, 'per': 4})
        # 识别正确返回语音二进制 错误则返回dict 参照下面错误码
        if not isinstance(result, dict):
            with open('audio.mp3', 'wb') as f:
                f.write(result)
                f.close()
            subprocess.call(["/usr/bin/afplay", os.getcwd()+"/audio.mp3"])

    def get_file_content(self, filePath):
        with open(filePath, 'rb') as fp:
            return fp.read()

    def send(self, request):
        response = getHtml(request)
        dic_json = json.loads(response)
        if "list" in dic_json:
            print '机器人: '.decode('utf-8') + dic_json["text"]
            if len(dic_json["list"]) > 0:
                for info in dic_json["list"]:
                    if "article" in info:
                        print '机器人: '.decode('utf-8') + \
                            info["article"] + \
                            " [ " + info["detailurl"] + " ]"
                    else:
                        print '机器人: '.decode('utf-8') + \
                            info["name"] + " [ " + info["detailurl"] + " ]"
        else:
            print '机器人: '.decode('utf-8') + dic_json["text"]
            self.speak(dic_json["text"])

    def say(self, key):
        api = 'http://www.tuling123.com/openapi/api?key=' + key + '&info='
        while True:
            info = raw_input('我: ')
            request = api + info
            if info == "say" :
            # 本地录音 -> 百度语音识别 -> 识别文本 -> 图灵机器人
                # 开始录音
                print "<开始录音>"
                self.rec.recoder()
                self.rec.savewav("me.wav")
                print "<结束录音>"
                # 开始语音识别
                result = self.client.asr(self.get_file_content('me.wav'), 'pcm', 16000, {'dev_pid': 1536})
                if result:
                    if result["err_no"] == 0:
                        # 发送图图灵机器人
                        print "语音识别成功:",",".join(result["result"])
                        request = api + ",".join(result["result"])
                        self.send(request)
                    else:
                        print "语音识别错误:", result
                else:
                    print "无法语音识别"
            elif info == "88" :
            # 退出程序
                print "机器人: ヾ(￣▽￣)Bye~Bye~"
                exit()
            else:
            # 本地文本 -> 图灵机器人
                self.send(request)


if __name__ == '__main__':
    fire.Fire(CocoBot)
