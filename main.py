# -*- coding: utf-8 -*-
import json
import requests
import time
import hashlib
import string
import random

# 米游社版本
app_version = "2.3.0"
act_id = "e202009291139501"
# 服务器
region = "cn_gf01"
# 设备号随意，但不能为空
device_id = "94581081EDD446EFAA3A45B8CC636CCF"
# 米游社cookie 换成自己的 推荐抓取手机版米游社cookie 电脑端的有效时间比较短，需要经常更换
cookie = '###'
# 原神uid 换成自己的
uid = '100000000'

headers = {}

# 发送企业微信消息
def send_message_QiYeVX(_message, useridlist):
    useridstr = "|".join(useridlist)
    # 企业微信agentid，自行更改
    agentid = '###'
    # 企业微信corpid，自行更改
    corpid = '###'
    # 企业微信corpsecret，自行更改
    corpsecret = '###'
    response = requests.get(f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={corpsecret}")
    data = json.loads(response.text)
    access_token = data['access_token']

    json_dict = {
       "touser" : useridstr,
       "msgtype" : "text",
       "agentid" : agentid,
       "text" : {
           "content" : _message
       },
       "safe": 0,
       "enable_id_trans": 0,
       "enable_duplicate_check": 0,
       "duplicate_check_interval": 1800
    }
    json_str = json.dumps(json_dict)
    response_send = requests.post(f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}", data=json_str)
    return json.loads(response_send.text)['errmsg'] == 'ok'

# 格式化文本信息，可以自行修改
def getText():
    # 签到
    signResult = json.loads(sign())
    gameInfo = json.loads(getGameInfo())["data"]["list"][0]
    # 游戏信息
    totalSignDay = json.loads(getTotalSignDay())["data"]
    totalSignDay = totalSignDay["total_sign_day"]
    signInfo = json.loads(getSignInfo())["data"]
    award = signInfo["awards"][totalSignDay - 1]
    dailyNote = json.loads(getDailyNote())["data"]
    # 方糖message内容，请不要格式化这段字符串
    message = '''
游戏昵称：{} 
签到结果：{} 
签到奖励：{} x {}
当前体力：{}/{}
树脂恢复时间：{}'''.format(
        gameInfo["nickname"],
        signResult['message'], award['name'], award['cnt'],
        dailyNote['current_resin'], dailyNote['max_resin'],
        secondToTime(dailyNote["resin_recovery_time"]))
    return message


# 设置请求头
def buildHearders():
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/{}".format(
            app_version), "Cookie": cookie, "x-rpc-device_id": device_id, "Host": "api-takumi.mihoyo.com",
        "Content-type": "application/json;charset=utf-8", "Accept": "application/json, text/plain, */*",
        "x-rpc-client_type": "5", "x-rpc-app_version": app_version, "DS": getDS(),
        "Referer": "https://webstatic.mihoyo.com/app/community-game-records/index.html?v=6",
        "X-Requested-With": "com.mihoyo.hyperion"}
    return headers


def md5(text):
    md5 = hashlib.md5()
    md5.update(text.encode())
    return md5.hexdigest()

# 生成DS校验码
def getDS():
    # n = 'cx2y9z9a29tfqvr1qsq6c7yz99b5jsqt' # v2.2.0 @Womsxd
    n = "h8w582wxwgqvahcdkpvdhbh2w9casgfl"
    i = str(int(time.time()))
    r = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
    c = md5("salt=" + n + "&t=" + i + "&r=" + r)
    return "{},{},{}".format(i, r, c)

# 生成每日任务DS校验码
def getDailyDS():
    br = ""
    s = "xV8v4Qu54lUKrEYFZkJhB8cuOh9Asafs"
    t = str(int(time.time()))
    r = str(random.randint(100000, 200000))
    c = md5("salt=" + s + "&t=" + t + "&r=" + r + "&b=" + br + "&q=" + "role_id=" + uid + "&server=" + region)
    res = "{},{},{}".format(t, r, c)
    return res


# 签到
def sign():
    signUrl = "https://api-takumi.mihoyo.com/event/bbs_sign_reward/sign"
    param = {"act_id": act_id, "region": region, "uid": uid}
    result = requests.request("POST", signUrl, headers=headers, data=json.dumps(param))
    return result.content.decode("utf-8")


# 获取签到信息
def getSignInfo():
    url = "https://api-takumi.mihoyo.com/event/bbs_sign_reward/home?act_id={}"
    userInfoResult = requests.get(url.format(act_id), headers=headers)
    return userInfoResult.content.decode("utf-8")


# 获取签到天数
def getTotalSignDay():
    url = "https://api-takumi.mihoyo.com/event/bbs_sign_reward/info?region={}&act_id={}&uid={}"
    userInfoResult = requests.get(url.format(region, act_id, uid), headers=headers)
    return userInfoResult.content.decode("utf-8")


# 获取游戏信息
def getGameInfo():
    url = "https://api-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie?game_biz=hk4e_cn"
    userInfoResult = requests.get(url, headers=headers)
    return userInfoResult.content.decode("utf-8")


# 获取原神米游社每月签到物品
def getMonthCheckinItem():
    url = "https://api-takumi.mihoyo.com/event/bbs_sign_reward/home?act_id={}"
    monthCheckinItem = requests.get(url.format(act_id), headers=headers)
    return monthCheckinItem.content.decode("utf-8")


# 获取米游社卡片
def getGameRecordCard():
    url = "https://api-takumi.mihoyo.com/game_record/card/wapi/getGameRecordCard?uid={}"
    monthCheckinItem = requests.get(url.format(cookieToDict(cookie)["account_id"]), headers=headers)
    return monthCheckinItem.content.decode("utf-8")


# 获取日常信息
def getDailyNote():
    url = 'https://api-takumi.mihoyo.com/game_record/app/genshin/api/dailyNote?server={}&role_id={}'
    headers["DS"] = getDailyDS()
    headers["x-rpc-app_version"] = "2.11.1"
    headers[
        "User-Agent"] = "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/{}".format(
        "2.11.1")
    dailyNoteResult = requests.get(url.format(region, uid), headers=headers)
    print(dailyNoteResult.content.decode("utf-8"))
    return dailyNoteResult.content.decode("utf-8")


# 获取原神角色信息
def getYsAvatars():
    headers["DS"] = getDailyDS()
    headers["x-rpc-app_version"] = "2.11.1"
    headers[
        "User-Agent"] = "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/{}".format(
        "2.11.1")
    url = "https://api-takumi.mihoyo.com/game_record/app/genshin/api/index?server={}&role_id={}"
    userInfoResult = requests.get(url.format(region, uid), headers=headers)
    return userInfoResult.content.decode("utf-8")

# 将cookie转化为字典形式
def cookieToDict(cookie):
    cookieDict = {}
    cookies = cookie.split("; ")
    for co in cookies:
        co = co.strip()
        p = co.split('=')
        value = co.replace(p[0] + '=', '').replace('"', '')
        cookieDict[p[0]] = value
    return cookieDict

# 秒数转化为时间
def secondToTime(second):
    re_time = second
    m, s = divmod(int(re_time), 60)
    h, m = divmod(m, 60)
    time = "%02d小时%02d分钟%02d秒" % (h, m, s)
    return time

# 云函数执行主函数
def main_handler(str1, str2):
    global headers
    headers = buildHearders()
    text = getText()
    send_message_QiYeVX(text)
    print(text)
    return 0
