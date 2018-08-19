# -*- coding: utf-8 -*-
import urllib
import json
import fire

from aip import AipSpeech  # 百度语音合成
import subprocess  # 调用命令行 afplay
import os
import config


def getHtml(url):
    page = urllib.urlopen(url)
    html = page.read()
    return html


class CocoBot(object):
    """A simple bot class."""

    def __init__(self):
        self.client = AipSpeech(config.APP_ID, config.API_KEY, config.SECRET_KEY)

    def speak(self, sentence):
        result = self.client.synthesis(sentence, 'zh', 1, {'vol': 5, 'per': 4})
        # 识别正确返回语音二进制 错误则返回dict 参照下面错误码
        if not isinstance(result, dict):
            with open('bot.mp3', 'wb') as f:
                f.write(result)
                f.close()
            subprocess.call(["/usr/bin/afplay", os.getcwd()+"/bot.mp3"])

    def say(self, key):
        api = 'http://www.tuling123.com/openapi/api?key=' + key + '&info='
        while True:
            info = raw_input('我: ')
            request = api + info
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


if __name__ == '__main__':
    fire.Fire(CocoBot)
