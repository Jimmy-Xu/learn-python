# -*- coding: utf-8 -*-

import urllib
import json
import fire

def getHtml(url):
    page = urllib.urlopen(url)
    html = page.read()
    return html


class CocoBot(object):
    """A simple bot class."""

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


if __name__ == '__main__':
    fire.Fire(CocoBot)
