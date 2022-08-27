import random
from time import localtime
from requests import get, post
from datetime import datetime, date, timedelta, timezone
from zhdate import ZhDate
import sys
import os


def get_color():
    # 获取随机颜色
    get_colors = lambda n: list(map(lambda i: "#" + "%06x" % random.randint(0, 0xFFFFFF), range(n)))
    color_list = get_colors(100)
    return random.choice(color_list)


def get_access_token():
    # appId
    app_id = config["app_id"]
    # appSecret
    app_secret = config["app_secret"]
    post_url = ("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}"
                .format(app_id, app_secret))
    try:
        access_token = get(post_url).json()['access_token']
    except KeyError:
        print("获取access_token失败，请检查app_id和app_secret是否正确")
        os.system("pause")
        sys.exit(1)
    # print(access_token)
    return access_token


def get_weather(region):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    key = config["weather_key"]
    region_url = "https://geoapi.qweather.com/v2/city/lookup?location={}&key={}".format(region, key)
    response = get(region_url, headers=headers).json()
    if response["code"] == "404":
        print("推送消息失败，请检查地区名是否有误！")
        os.system("pause")
        sys.exit(1)
    elif response["code"] == "401":
        print("推送消息失败，请检查和风天气key是否正确！")
        os.system("pause")
        sys.exit(1)
    else:
        # 获取地区的location--id
        location_id = response["location"][0]["id"]
    weather_url = "https://devapi.qweather.com/v7/weather/now?location={}&key={}".format(location_id, key)
    response = get(weather_url, headers=headers).json()
    # 天气
    weather = response["now"]["text"]
    # 当前温度
    temp = response["now"]["temp"] + u"\N{DEGREE SIGN}" + "C"
    # 风向
    wind_dir = response["now"]["windDir"]
    return weather, temp, wind_dir


def get_birthday(birthday, year, today):
    birthday_year = birthday.split("-")[0]
    # 判断是否为农历生日
    if birthday_year[0] == "r":
        r_mouth = int(birthday.split("-")[1])
        r_day = int(birthday.split("-")[2])
        # 获取农历生日的今年对应的月和日
        try:
            birthday = ZhDate(year, r_mouth, r_day).to_datetime().date()
        except TypeError:
            print("请检查生日的日子是否在今年存在")
            os.system("pause")
            sys.exit(1)
        birthday_month = birthday.month
        birthday_day = birthday.day
        # 今年生日
        year_date = date(year, birthday_month, birthday_day)

    else:
        # 获取国历生日的今年对应月和日
        birthday_month = int(birthday.split("-")[1])
        birthday_day = int(birthday.split("-")[2])
        # 今年生日
        year_date = date(year, birthday_month, birthday_day)
    # 计算生日年份，如果还没过，按当年减，如果过了需要+1
    if today > year_date:
        if birthday_year[0] == "r":
            # 获取农历明年生日的月和日
            r_last_birthday = ZhDate((year + 1), r_mouth, r_day).to_datetime().date()
            birth_date = date((year + 1), r_last_birthday.month, r_last_birthday.day)
        else:
            birth_date = date((year + 1), birthday_month, birthday_day)
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    elif today == year_date:
        birth_day = 0
    else:
        birth_date = year_date
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    return birth_day


def get_today_day(num, note_en):
    if num == 0:
        note_en = "一定要好好享受周末的最后一天！不要老是想着明天要上班了就emo,珍惜今天！"
    elif num == 1:
        note_en = "又要开始上班啦，又有钱钱拿"
    elif num == 2:
        note_en = "今天是个好日子，也不知道昨天的班上的怎么样。希望今天也有好运气"
    elif num == 3:
        note_en = "马上一周就要过去一半啦，今天回家吃点香香的"
    elif num == 4:
        note_en = "再挺两天就周末啦,周四也是要好好上班的一天"
    elif num == 5:
        note_en = "周五啦！再过几个小时就可以享受周末咯"
    elif num == 6:
        note_en = "美好的一天开始啦，你这个小猪仔现在肯定还没起床"
    else:
        note_en = "出错啦,再等等我修复吧"
    # 微信平台配置
    return note_en


def get_ciba_en():
    url = "http://open.iciba.com/dsapi/"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    r = get(url, headers=headers)
    note_en = r.json()["content"]
    return note_en


def get_ciba_ch():
    url = "http://open.iciba.com/dsapi/"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    r = get(url, headers=headers)
    note_ch = r.json()["note"]
    return note_ch


# 根据时间打招呼
def get_greet_note(greet_note, time, isDayOff):
    if 8 <= time & time <= 9:
        greet_note = "早上好呀，今天也是活力满满的一天"
    elif 12 <= time & time <= 13:
        greet_note = "中午啦，有没有好好吃饭鸭"
    elif 17 <= time & time <= 18:
        greet_note = "终于休息咯，快回家躺在床上当个咸鱼吧"
    elif 23 <= time & isDayOff:
        greet_note = "快起来玩游戏啦，当然也别忘了要好好休息，周末愉快，努力把把吃鸡"
    elif 23 <= time & isDayOff == False:
        greet_note = "该睡觉啦，放下手机订好闹钟，明天还是打工人的一天，晚安"
    else:
        greet_note = "今日份播报来啦"
    return greet_note


# 随机表情
def get_random_emoji(emoji):
    emojiList = ["♡(*ฅˊ˘ˋฅ*)♡", "(๑ `▽´๑)", "(*´°`*)", "꒰*´◒`*꒱", "ॱଳॱ", "꒳ᵒ꒳ᵎᵎᵎ", "๐˙Ⱉ˙๐", "( ๑ˊ•̥▵•)੭₎₎",
                 " ⁄(⁄⁄•⁄ω⁄•⁄⁄)⁄ ", "(⑉･⌓･⑉)", "(⑉･-･⑉)", "꒰ᐢ⸝⸝•༝•⸝⸝ᐢ꒱", "( ᐖ )", "(˶˚ ᗨ ˚˶)", "(๑•̀ㅂ•́)", "(๑˃́ꇴ˂̀๑)",
                 "(๑ `▽´๑)", "✧(๑•̀ㅁ•́ฅ)", "(๑ ๑)♡", "*ଘ(♡⸝⸝•༝•⸝⸝)੭", "*ଘ(੭*ˊᵕˋ)੭* ੈ♡‧₊˚", "(୨୧•͈ᴗ•͈)", "(•̀ᴗ•́)",
                 " ʕ๑•ɷ•๑ʔ"]
    emoji = emojiList[random.randint(0, len(emojiList) - 1)]
    return emoji


def send_message(to_user, access_token, region_name, weather, temp, wind_dir, note_ch, note_en, extra_msg,
                 handwrite_msg, greet_note):
    url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(access_token)

    # 根据日期计算星期几
    week_list = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"]

    # 手动转换时间
    # EST 冬令时了需要修改
    utc = timezone.utc
    utc_time = datetime.utcnow().replace(tzinfo=utc)
    toronto_time = timezone(timedelta(hours=-4))
    # 多伦多冬令时时间 可以跟据自己时区修改
    # toronto_time = timezone(timedelta(hours=-5))
    curr_time = utc_time.astimezone(toronto_time)

    year = curr_time.year
    today = curr_time.date()
    week = week_list[today.isoweekday() % 7]

    # 时间更换打招呼
    if today.isoweekday() % 7 >= 5:
        greet_note = get_greet_note(greet_note, curr_time.hour, True)
    else:
        greet_note = get_greet_note(greet_note, curr_time.hour, False)

    # 根据星期几 发送不同的配置句子
    # extra_msg = get_today_day(today.isoweekday() % 7, extra_msg)
    extra_msg = curr_time.time()
    # 获取在一起的日子的日期格式
    love_year = int(config["love_date"].split("-")[0])
    love_month = int(config["love_date"].split("-")[1])
    love_day = int(config["love_date"].split("-")[2])
    love_date = date(love_year, love_month, love_day)
    # 获取在一起的日期差
    love_days = str(today.__sub__(love_date)).split(" ")[0]

    # 获取所有生日数据
    birthdays = {}
    for k, v in config.items():
        if k[0:5] == "birth":
            birthdays[k] = v

    emoji = "CUTE EMOJI"
    # 发送数据
    data = {
        "touser": to_user,
        "template_id": config["template_id"],
        "url": "http://weixin.qq.com/download",
        "topcolor": "#99F5F1",
        "data": {
            "date": {
                "value": "{} {}".format(today, week),
                "color": get_color()
            },
            "region": {
                "value": region_name,
                "color": get_color()
            },
            "weather": {
                "value": weather,
                "color": get_color()
            },
            "temp": {
                "value": temp,
                "color": get_color()
            },
            "wind_dir": {
                "value": wind_dir,
                "color": get_color()
            },
            "love_day": {
                "value": love_days,
                "color": get_color()
            },
            "note_en": {
                "value": note_en,
                "color": get_color()
            },
            "note_ch": {
                "value": note_ch,
                "color": get_color()
            },
            "extra_msg": {
                "value": "{} {}".format(extra_msg, str(get_random_emoji(emoji))),
                "color": get_color()
            },
            "greet_note": {
                "value": "{} {} {}".format(str(get_random_emoji(emoji)), greet_note, str(get_random_emoji(emoji))),
                # "value":  greet_note,
                "color": get_color()
            },
            "handwrite_msg": {
                "value": handwrite_msg,
                "color": get_color()
            }
        }
    }
    for key, value in birthdays.items():
        # 获取距离下次生日的时间
        birth_day = get_birthday(value["birthday"], year, today)
        if birth_day == 0:
            birthday_data = "今天{}生日哦，祝{}生日快乐！".format(value["name"], value["name"])
        else:
            birthday_data = "距离{}的生日还有{}天".format(value["name"], birth_day)
        # 将生日数据插入data
        data["data"][key] = {"value": birthday_data, "color": get_color()}
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }

    # 推送
    response = post(url, headers=headers, json=data).json()
    if response["errcode"] == 40037:
        print("推送消息失败，请检查模板id是否正确")
    elif response["errcode"] == 40036:
        print("推送消息失败，请检查模板id是否为空")
    elif response["errcode"] == 40003:
        print("推送消息失败，请检查微信号是否正确")
    elif response["errcode"] == 0:
        print("推送消息成功")
    else:
        print(response)


if __name__ == "__main__":
    try:
        with open("config.txt", encoding="utf-8") as f:
            config = eval(f.read())
    except FileNotFoundError:
        print("推送消息失败，请检查config.txt文件是否与程序位于同一路径")
        os.system("pause")
        sys.exit(1)
    except SyntaxError:
        print("推送消息失败，请检查配置文件格式是否正确")
        os.system("pause")
        sys.exit(1)

    # 获取accessToken
    accessToken = get_access_token()
    # 接收的用户
    users = config["user"]
    # 传入地区获取天气信息
    region = config["region"]
    weather, temp, wind_dir = get_weather(region)
    note_ch = config["note_ch"]
    note_en = config["note_en"]
    extra_msg = config["extra_msg"]
    handwrite_msg = config["handwrite_msg"]
    greet_note = config["greet_note"]

    # 每日金句 中/英语
    if note_ch == "":
        note_ch = get_ciba_ch()
    if note_en == "":
        note_en = get_ciba_en()

    # 公众号推送消息
    for user in users:
        send_message(user, accessToken, region, weather, temp, wind_dir, note_ch, note_en, extra_msg, handwrite_msg,
                     greet_note)
    os.system("pause")
