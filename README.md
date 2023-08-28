# Nuit-Library-Seats
fork: https://github.com/bear-zd/ChaoXingReserveSeat

## setting 
before running the script , you should install a package `pip install pycrypto`

and edit the config.json to make this script work.

##  addition
添加签到功能，每次启动默认为当前用户签到，可以在配置文件中修改sign=0来取消签到

```json
{
  "settings": {
    "SYS_SLEEP_TIME": 1, // 每个帐号抢的间隔
    "SYS_END_TIME": "22:01:00" // 抢座位的截止时间
  },
  "reserve": [
    {
      "username": "username",
      "password": "password",
      "sign": 1, // 是否自动签到
      "day": 1, // 0:今天，1:明天，2:后天，以此类推
      "roomid": "6993", // 房间编号
      "seatid": [
        "105" // 座位编号
      ],
      "time": [
        ["8:30", "12:30"],
        ["12:30", "16:30"],
        ["16:30", "20:30"],
        ["20:30", "22:00"]
      ],
      "wait_time": 1, // 每次抢time中的时间间隔，实测东软1s间隔不会有太大问题
      "flag": 0 // 是否需要反复抢，东软基本上没人跟你抢。。
    }
  ]
}

```
What you should do is just set a crontab on your server to run this script.

## running

Use `python main.py` to run this script, add arguement `-u config.json` to point the config file posision

In linux/macos , you can just set a crontab : `crontab -e` and add the command :
`0 8 * * * cd ~/Desktop/pythonProject/Nuit-Library-Seats && source venv/bin/activate && python3 main.py >> log.txt 2>&1`

每早八点定时跑脚本


In windows, you can add a time task:

![](https://zideapicbed.oss-cn-shanghai.aliyuncs.com/QQ%E5%9B%BE%E7%89%8720221120213736.png)