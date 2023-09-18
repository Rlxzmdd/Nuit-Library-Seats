import json
import base64
import requests
import re
from binascii import b2a_hex, a2b_hex, b2a_base64
import time
import datetime
import json

from Crypto.Cipher import AES
from urllib3.exceptions import InsecureRequestWarning
import argparse
import os
import execjs

SYS_SLEEP_TIME = 1
SYS_END_TIME = "22:01:00"

BLOCK_SIZE = 16  # Bytes


def get_enc(data):
    with open('./enc.js', encoding='utf-8') as f:
        js = f.read()

        # 通过compile命令转成一个js对象
    docjs = execjs.compile(js)

    # 调用function
    res = docjs.call('getMd5Hash', data)
    return res


def pad(s): return s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * \
    chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)


def unpad(s): return s[:-ord(s[len(s) - 1:])]


def AES_Encrypt(data):
    vi = "u2oh6Vu^HWe4_AES"
    key = "u2oh6Vu^HWe4_AES"
    data = pad(data)  # 字符串补位
    cipher = AES.new(key.encode('utf8'), AES.MODE_CBC, vi.encode('utf8'))
    # 加密后得到的是bytes类型的数据，使用Base64进行编码,返回byte字符串
    encryptedbytes = cipher.encrypt(data.encode('utf8'))
    encodestrs = base64.b64encode(encryptedbytes)  # 对byte字符串按utf-8进行解码
    enctext = encodestrs.decode('utf8')
    return enctext


class reserve:
    def __init__(self):
        self.login_page = "https://passport2.chaoxing.com/mlogin?loginType=1&newversion=true&fid="
        self.url = "https://office.chaoxing.com/front/third/apps/seat/code?id={}&seatNum={}"
        self.submit_url = "https://office.chaoxing.com/data/apps/seat/submit"
        self.seat_url = "https://office.chaoxing.com/data/apps/seat/getusedtimes"
        self.login_url = "https://passport2.chaoxing.com/fanyalogin"
        self.token = ""
        self.success_times = 0
        self.fail_dict = []
        self.submit_msg = []
        self.requests = requests.session()
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.3 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1 wechatdevtools/1.05.2109131 MicroMessenger/8.0.5 Language/zh_CN webview/16364215743155638",
            "X-Requested-With": "com.tencent.mm"
        }
        self.login_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.3 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1 wechatdevtools/1.05.2109131 MicroMessenger/8.0.5 Language/zh_CN webview/16364215743155638",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "passport2.chaoxing.com"
        }
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    def get_html(self, url):
        response = self.requests.get(url=url, verify=False)
        html = response.content.decode('utf-8')
        token = re.findall(
            'token: \'(.*?)\'', html)[0] if len(re.findall('token: \'(.*?)\'', html)) > 0 else ""

        return token

    def get_login_status(self):
        self.requests.headers = self.login_headers
        self.requests.get(url=self.login_page, verify=False)

    def get_submit(self, url, need_day, seat, token, roomid, seatid, captcha):
        day = datetime.date.today() + datetime.timedelta(days=need_day)
        # 0:预约今天，1:明天，2:后天
        parm0 = {
            "roomId": roomid,
            "day": str(day),
            "startTime": seat[0],
            "endTime": seat[1],
            "seatNum": seatid,
            "token": token,
            "captcha": "",
            "type": 1
        }
        enc = get_enc(parm0)
        parm = {
            "roomId": roomid,
            "day": str(day),
            "startTime": seat[0],
            "endTime": seat[1],
            "seatNum": seatid,
            "token": token,
            "captcha": "",
            "type": 1,
            "enc": enc
        }
        html = self.requests.post(
            url=url, params=parm, verify=False).content.decode('utf-8')
        self.submit_msg.append(
            seat[0] + "~" + seat[1] + ':  ' + str(json.loads(html)))
        if json.loads(html)['success']:
            print("[true]成功抢座: {},{}".format(seatid, seat))
        else:
            print("[false]抢座失败: {},{} --- {}".format(seatid, seat, json.loads(html)))

        return json.loads(html)["success"]

    def login(self, username, password):
        username = AES_Encrypt(username)
        password = AES_Encrypt(password)
        parm = {
            "fid": -1,
            "uname": username,
            "password": password,
            "refer": "http%3A%2F%2Foffice.chaoxing.com%2Ffront%2Fthird%2Fapps%2Fseat%2Fcode%3Fid%3D4219%26seatNum%3D380",
            "t": True
        }
        jsons = self.requests.post(
            url=self.login_url, params=parm, verify=False)
        obj = jsons.json()
        if obj['status']:
            return (True, '')
        else:
            return (False, obj['msg2'])

    def submit(self, day, i, wait_time, roomid, seatid):
        for seat in seatid:
            suc = False
            remaining_times_for_seat = 1  # 每一个的座位尝试次数
            while ~suc and remaining_times_for_seat > 0:
                for times in i:
                    token = self.get_html(self.url.format(roomid, seat))
                    suc = self.get_submit(self.submit_url, day, times, token, roomid, seat, 0)
                    time.sleep(wait_time)
                if suc:
                    return suc
                time.sleep(SYS_SLEEP_TIME)
                remaining_times_for_seat -= 1
        return suc

    def sign(self, current_date):
        sign_data = self.get_my_seat_id(current_date)
        need_sign_data = []
        for index in sign_data:
            if index['status'] == 1:
                print("[exist]今日已签: {}".format(
                    index['firstLevelName'] + index['secondLevelName'] + index['thirdLevelName'] + index['seatNum']))
            if index['status'] == 0 or index['status'] == 3 or index['status'] == 5:
                need_sign_data.append(index)
                continue
        if need_sign_data:
            for need_sign in need_sign_data:
                response = self.requests.get(
                    url='https://office.chaoxing.com/data/apps/seat/sign?id={}'.format(need_sign["id"]))
                location = need_sign['firstLevelName'] + need_sign['secondLevelName'] + need_sign['thirdLevelName'] + \
                           need_sign['seatNum']
                if response.json()['success']:
                    print("[true]成功签到: {}".format(location))
                else:
                    print("[false]签到失败: {}\n反馈信息: {}".format(location, response.json()['msg']))
        else:
            print("[none]今日没有需要签到的数据")

    def get_my_seat_id(self, current_date):
        response = self.requests.get(url='https://office.chaoxing.com/data/apps/seat/reservelist?'
                                         'indexId=0&'
                                         'pageSize=100&'
                                         'type=-1').json()['data']['reserveList']
        result = []
        for index in response:
            if index['type'] == -1:
                if index['today'] == current_date:
                    # 今日签到信息
                    result.append(index)
        return result


def main(users):
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    current_time = time.strftime("%H:%M:%S", time.localtime())
    suc = False
    print(current_time, SYS_END_TIME)

    while current_time < SYS_END_TIME:
        if len(users) == 0:
            print("--- 结束 ---")
            return
        for user in users:
            username, password, sign, day, times, wait_time, roomid, seatid, flag = user.values()
            s = reserve()
            s.get_login_status()
            s.login(username, password)
            s.requests.headers.update({'Host': 'office.chaoxing.com'})
            if sign:
                s.sign(current_date)
                # 签到今日座位
            suc = s.submit(day, times, wait_time, roomid, seatid)
            # 支持1个人抢座 多个人需要把return去了
            if flag:
                if suc:
                    return
            else:
                users.remove(user)

        current_time = time.strftime("%H:%M:%S", time.localtime())


if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    parser = argparse.ArgumentParser(prog='Chao Xing seat auto reserve')
    parser.add_argument('-u', '--user', default=config_path, help='user config file')
    args = parser.parse_args()
    with open(args.user, "r+") as data:
        settings = json.load(data)
        SYS_SLEEP_TIME = settings["settings"]["SYS_SLEEP_TIME"]
        SYS_END_TIME = settings["settings"]["SYS_END_TIME"]
        users_data = settings["reserve"]
    main(users_data)
