tuling 聊天机器人
------------------

# dependency

```
$ brew install portaudio
$ sudo pip install fire baidu-aip pyaudio
```

# usage

```
//文本聊天
$ python cocobot_v1.py say --key=<key of tuling123>

//机器人答复采用百度语音合成
$ python cocobot_v2.py say --key=<key of tuling123>

//语音聊天
$ python cocobot_v3.py say --key=<key of tuling123>
```