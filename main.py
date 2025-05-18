import tomllib
import aiohttp
from loguru import logger
import random
from PIL import Image, ImageDraw, ImageFont
from zhdate import ZhDate as lunar_date
import time
import datetime
import os
import io

from WechatAPI import WechatAPIClient
from utils.decorators import *
from utils.plugin_base import PluginBase


class Moyu(PluginBase):
    description = "Felix摸鱼提醒小助手"
    author = "Felix"
    version = "1.0.0"

    def __init__(self):
        super().__init__()
        with open("plugins/Moyu/config.toml", "rb") as f:
            plugin_config = tomllib.load(f)
        config = plugin_config["Moyu"]
        self.enable = config["enable"]
        self.command = config["commands"]
        self.priority = config["priority"]


    @on_text_message(priority=60)  # 遵循文档建议
    async def handle_text(self, bot: WechatAPIClient, message: dict) -> bool:  # 添加类型提示
        """处理文本消息，实现摸鱼功能."""
        if not self.enable:
            return True  # 插件未启用，允许其他插件处理

        content = str(message["Content"]).strip()
        command = content.split(" ")

        if command[0] not in self.command:
            return True
        try:
            if command[0] in self.command:
                current_path = os.path.dirname(__file__)
                current_list_path = current_path.split('\\')[0:-1]
                fileCachePath = '/'.join(current_list_path) + '/Moyu'
                savePath = fileCachePath + '/image/' + str(int(time.time() * 1000)) + '.png'
                # 创建一个新的Image对象
                bgimg = Image.new(mode='RGB', size=(480, 800), color="#FFFFFF")
                choice = random.randint(1, 100)
                isGetFish = False
                if choice % 2 == 0:
                    files = os.listdir(f"{fileCachePath}/picture/")
                    # print(files)
                    fishImgName = random.choice(files)
                    fish_img = Image.open(f"{fileCachePath}/picture/" + fishImgName)
                    fish_img = fish_img.resize((480, 280))
                    ################title##################
                    # 创建 ImageDraw 对象 , 标题
                    title_bgimg = ImageDraw.Draw(fish_img)
                    # 以左上角为原点，绘制矩形。元组坐标序列表示矩形的位置、大小；fill设置填充色为红色，outline设置边框线为黑色
                    title_bgimg.rectangle((163, 232, 318, 272), fill=(255, 127, 107), outline=(255, 127, 107))
                    # 加载计算机本地字体文件
                    font = ImageFont.truetype(f'{fileCachePath}/msyh.ttc', size=18)
                    # 在原图像上添加文本
                    title_bgimg.text(xy=(178, 240), text='提醒摸鱼小助手', fill=(255, 255, 255), font=font)
                    #################END####################
                    isGetFish = True
                    Image.Image.paste(bgimg, fish_img, (0, 0))
                    logger.debug("摸到鱼了")
                else:
                    ################title##################
                    # 创建 ImageDraw 对象 , 标题
                    title_bgimg = ImageDraw.Draw(bgimg)
                    # 以左上角为原点，绘制矩形。元组坐标序列表示矩形的位置、大小；fill设置填充色为红色，outline设置边框线为黑色
                    title_bgimg.rectangle((163, 232, 318, 272), fill=(255, 127, 107), outline=(255, 127, 107))
                    # 加载计算机本地字体文件
                    font = ImageFont.truetype(f'{fileCachePath}/msyh.ttc', size=18)
                    # 在原图像上添加文本
                    title_bgimg.text(xy=(178, 240), text='提醒摸鱼小助手', fill=(255, 255, 255), font=font)
                    #################END####################
                    isGetFish = False
                    logger.debug("没有摸到鱼")

                template = Image.open(f'{fileCachePath}/template.jpg')
                Alltext = ImageDraw.Draw(template)
                font1 = ImageFont.truetype(f'{fileCachePath}/msyh.ttc', size=16)

                # 统计中文和非中文字数
                cnCount = 0
                otherCount = 0

                # 获取发送人昵称
                # 优先从contacts.db获取昵称
                local_nickname = bot.get_local_nickname(message["FromWxid"], message["SenderWxid"])
                if local_nickname:
                    sName = local_nickname
                    logger.debug(f"使用本地数据库昵称 @{local_nickname}")
                else:
                    # 如果本地数据库没有，再通过API获取
                    sName = await bot.get_nickname(message["SenderWxid"])
                    logger.debug(f"使用API昵称 @{sName}")

                # 判断摸鱼昵称
                if sName != None:
                    if str == type(sName):
                        for str_tmp in sName:
                            if ord(str_tmp) - ord('0') >= 128:
                                cnCount += 1
                            else:
                                otherCount += 1
                else:
                    return None

                # 是否摸到鱼
                if isGetFish:
                    # 一个中文占18px空隙。非中文占10px
                    if sName == "" or sName == None:
                        Alltext.text(xy=(49, 20), text=sName, fill=(70, 81, 232), font=font1)
                    else:
                        Alltext.text(xy=(49, 20), text=sName, fill=(70, 81, 232), font=font1)
                    Alltext.text(xy=(49 + (cnCount * 18) + (otherCount * 10), 20), text='摸到了一条', fill=(0, 0, 0),
                                 font=font1)
                    fishName = fishImgName.rstrip('.jpg')
                    Alltext.text(xy=(49 + (cnCount * 18) + (otherCount * 10) + (5 * 18), 20), text=fishName,
                                 fill=(203, 2, 25), font=font1)
                else:
                    # 一个中文占18px空隙。非中文占10px
                    if sName == "" or sName == None:
                        Alltext.text(xy=(49, 20), text=sName, fill=(70, 81, 232), font=font1)
                    else:
                        Alltext.text(xy=(49, 20), text=sName, fill=(70, 81, 232), font=font1)
                    Alltext.text(xy=(49 + (cnCount * 18) + (otherCount * 10), 20), text='本次未摸到鱼', fill=(0, 0, 0),
                                 font=font1)

                # 时间
                nowDate = datetime.datetime.now()
                theDate = nowDate.strftime('%m月%d日')
                weekDict = {'0': '周日', '1': '周一', '2': '周二', '3': '周三', '4': '周四', '5': '周五', '6': '周六'}
                weekCN = weekDict[nowDate.strftime('%w')]
                today0H = nowDate.replace(hour=0, minute=0, second=0, microsecond=0)
                today6H = nowDate.replace(hour=6, minute=0, second=0, microsecond=0)
                today9H = nowDate.replace(hour=9, minute=0, second=0, microsecond=0)
                today11H = nowDate.replace(hour=11, minute=0, second=0, microsecond=0)
                today13H = nowDate.replace(hour=13, minute=0, second=0, microsecond=0)
                today18H = nowDate.replace(hour=18, minute=0, second=0, microsecond=0)
                today19H = nowDate.replace(hour=19, minute=0, second=0, microsecond=0)
                # today20H = nowDate.replace(hour=20, minute=0, second=0, microsecond=0)
                moment = ''
                if (nowDate >= today0H) and nowDate < today6H:
                    moment = "凌晨"
                elif (nowDate >= today6H) and nowDate < today11H:
                    moment = "上午"
                elif (nowDate >= today11H) and nowDate < today13H:
                    moment = "中午"
                elif (nowDate >= today13H) and nowDate < today18H:
                    moment = "下午"
                elif (nowDate >= today18H) and nowDate < today19H:
                    moment = "傍晚"
                elif nowDate > today19H:
                    moment = "晚上"

                Alltext.text(xy=(179, 119), text=theDate + weekCN + moment, fill=(0, 237, 0), font=font1)

                # 下班
                dictTime = {}
                if (nowDate >= today9H) and nowDate < today18H:
                    timeTotolSec = (today18H - nowDate).seconds
                    if timeTotolSec > 0 and timeTotolSec < 60:
                        dictTime['hours'] = 0
                        dictTime['minutes'] = 0
                    else:
                        timeMin = timeTotolSec // 60
                        if ((timeMin / 60) >= 1) and ((timeMin % 60) != 0):
                            dictTime['hours'] = timeMin // 60
                            dictTime['minutes'] = timeMin % 60
                        else:
                            dictTime['hours'] = 0
                            dictTime['minutes'] = timeMin
                else:
                    dictTime['hours'] = 0
                    dictTime['minutes'] = 0
                ### 小时
                font2 = ImageFont.truetype(f'{fileCachePath}/digital-7-mono-3.ttf', size=22)
                if len(str(dictTime['hours'])) == 1:
                    Alltext.text(xy=(162, 223), text=str(dictTime['hours']), fill=(255, 0, 0), font=font2)
                elif len(str(dictTime['hours'])) == 2:
                    Alltext.text(xy=(162, 223), text=str(dictTime['hours'])[1], fill=(255, 0, 0), font=font2)
                    Alltext.text(xy=(162 - 11, 223), text=str(dictTime['hours'])[0], fill=(255, 0, 0), font=font2)
                else:
                    # 防止不可预知的bug报错
                    Alltext.text(xy=(162, 223), text='?', fill=(255, 0, 0), font=font2)
                # Alltext.text(xy=(162 - 11, 223), text='5', fill=(255, 0, 0), font=font2)
                # Alltext.text(xy=(162 - 11 - 11, 223), text='0', fill=(255, 0, 0), font=font2)

                ### 分钟
                if len(str(dictTime['minutes'])) == 1:
                    Alltext.text(xy=(162 + 16 + 16 + 16 + 15, 223), text=str(dictTime['minutes']), fill=(255, 0, 0),
                                 font=font2)
                elif len(str(dictTime['minutes'])) == 2:
                    Alltext.text(xy=(162 + 16 + 16 + 16 + 15, 223), text=str(dictTime['minutes'])[1], fill=(255, 0, 0),
                                 font=font2)
                    Alltext.text(xy=(162 + 16 + 16 + 16 + 15 - 11, 223), text=str(dictTime['minutes'])[0], fill=(255, 0, 0),
                                 font=font2)
                # 周末
                # font2=ImageFont.truetype('digital-7-mono-3.ttf',size=22)
                if nowDate.strftime('%w') != '0':
                    Alltext.text(xy=(162, 248), text=str(6 - int(nowDate.strftime('%w'))), fill=(255, 0, 0), font=font2)
                else:
                    Alltext.text(xy=(162, 248), text='0', fill=(255, 0, 0), font=font2)
                    # Alltext.text(xy=(162 - 11, 248), text='5', fill=(255, 0, 0), font=font2)
                    # Alltext.text(xy=(162 - 11 - 11, 248), text='0', fill=(255, 0, 0), font=font2)

                #
                today = datetime.date.today()

                if today > lunar_date(today.year, 1, 1).to_datetime().date():
                    distance_big_year = (lunar_date(today.year + 1, 1, 1).to_datetime().date() - today).days
                else:
                    distance_big_year = (lunar_date(today.year, 1, 1).to_datetime().date() - today).days

                # 计算端午节
                distance_5_5 = (lunar_date(today.year, 5, 5).to_datetime().date() - today).days
                distance_5_5 = distance_5_5 if distance_5_5 > 0 else (
                            lunar_date(today.year + 1, 5, 5).to_datetime().date() - today).days
                # 计算中秋节
                distance_8_15 = (lunar_date(today.year, 8, 15).to_datetime().date() - today).days
                distance_8_15 = distance_8_15 if distance_8_15 > 0 else (
                            lunar_date(today.year + 1, 8, 15).to_datetime().date() - today).days
                # 计算元旦节
                distance_year = (datetime.datetime.strptime(f"{today.year + 1}-01-01", "%Y-%m-%d").date() - today).days
                # 计算清明节
                distance_4_5 = (datetime.datetime.strptime(f"{today.year}-04-05", "%Y-%m-%d").date() - today).days
                distance_4_5 = distance_4_5 if distance_4_5 > 0 else (
                            datetime.datetime.strptime(f"{today.year + 1}-04-05", "%Y-%m-%d").date() - today).days
                # 计算劳动节
                distance_5_1 = (datetime.datetime.strptime(f"{today.year}-05-01", "%Y-%m-%d").date() - today).days
                distance_5_1 = distance_5_1 if distance_5_1 > 0 else (
                            datetime.datetime.strptime(f"{today.year + 1}-05-01", "%Y-%m-%d").date() - today).days
                # 计算国庆节
                distance_10_1 = (datetime.datetime.strptime(f"{today.year}-10-01", "%Y-%m-%d").date() - today).days
                distance_10_1 = distance_10_1 if distance_10_1 > 0 else (
                            datetime.datetime.strptime(f"{today.year + 1}-10-01", "%Y-%m-%d").date() - today).days

                time_ = {
                    'chunjie': distance_big_year,
                    'qingming': distance_4_5,
                    'laodong': distance_5_1,
                    'duanwu': distance_5_5,
                    'zhongqiu': distance_8_15,
                    'guoqing': distance_10_1,
                    'yuandan': distance_year
                }

                # 春节倒计时
                if len(str(time_['chunjie'])) == 1:
                    Alltext.text(xy=(162, 248 + 25), text=str(time_['chunjie']), fill=(255, 0, 0), font=font2)
                elif len(str(time_['chunjie'])) == 2:
                    Alltext.text(xy=(162, 248 + 25), text=str(time_['chunjie'])[1], fill=(255, 0, 0), font=font2)
                    Alltext.text(xy=(162 - 11, 248 + 25), text=str(time_['chunjie'])[0], fill=(255, 0, 0), font=font2)
                elif len(str(time_['chunjie'])) == 3:
                    Alltext.text(xy=(162, 248 + 25), text=str(time_['chunjie'])[2], fill=(255, 0, 0), font=font2)
                    Alltext.text(xy=(162 - 11, 248 + 25), text=str(time_['chunjie'])[1], fill=(255, 0, 0), font=font2)
                    Alltext.text(xy=(162 - 11 - 11, 248 + 25), text=str(time_['chunjie'])[0], fill=(255, 0, 0), font=font2)
                else:
                    Alltext.text(xy=(162, 248 + 25), text='?', fill=(255, 0, 0), font=font2)

                # 清明节倒计时
                if len(str(time_['qingming'])) == 1:
                    Alltext.text(xy=(162, 248 + 25 + 25), text=str(time_['qingming']), fill=(255, 0, 0), font=font2)
                elif len(str(time_['qingming'])) == 2:
                    Alltext.text(xy=(162, 248 + 25 + 25), text=str(time_['qingming'])[1], fill=(255, 0, 0), font=font2)
                    Alltext.text(xy=(162 - 11, 248 + 25 + 25), text=str(time_['qingming'])[0], fill=(255, 0, 0), font=font2)
                elif len(str(time_['qingming'])) == 3:
                    Alltext.text(xy=(162, 248 + 25 + 25), text=str(time_['qingming'])[2], fill=(255, 0, 0), font=font2)
                    Alltext.text(xy=(162 - 11, 248 + 25 + 25), text=str(time_['qingming'])[1], fill=(255, 0, 0), font=font2)
                    Alltext.text(xy=(162 - 11 - 11, 248 + 25 + 25), text=str(time_['qingming'])[0], fill=(255, 0, 0),
                                 font=font2)

                # 劳动节倒计时
                if len(str(time_['laodong'])) == 1:
                    Alltext.text(xy=(162, 248 + 25 + 25 + 26), text=str(time_['laodong']), fill=(255, 0, 0), font=font2)
                elif len(str(time_['laodong'])) == 2:
                    Alltext.text(xy=(162, 248 + 25 + 25 + 26), text=str(time_['laodong'])[1], fill=(255, 0, 0), font=font2)
                    Alltext.text(xy=(162 - 11, 248 + 25 + 25 + 26), text=str(time_['laodong'])[0], fill=(255, 0, 0),
                                 font=font2)
                elif len(str(time_['laodong'])) == 3:
                    Alltext.text(xy=(162, 248 + 25 + 25 + 26), text=str(time_['laodong'])[2], fill=(255, 0, 0), font=font2)
                    Alltext.text(xy=(162 - 11, 248 + 25 + 25 + 26), text=str(time_['laodong'])[1], fill=(255, 0, 0),
                                 font=font2)
                    Alltext.text(xy=(162 - 11 - 11, 248 + 25 + 25 + 26), text=str(time_['laodong'])[0], fill=(255, 0, 0),
                                 font=font2)

                # 端午节倒计时
                if len(str(time_['duanwu'])) == 1:
                    Alltext.text(xy=(162, 248 + 25 + 25 + 26 + 26), text=str(time_['duanwu']), fill=(255, 0, 0), font=font2)
                elif len(str(time_['duanwu'])) == 2:
                    Alltext.text(xy=(162, 248 + 25 + 25 + 26 + 26), text=str(time_['duanwu'])[1], fill=(255, 0, 0),
                                 font=font2)
                    Alltext.text(xy=(162 - 11, 248 + 25 + 25 + 26 + 26), text=str(time_['duanwu'])[0], fill=(255, 0, 0),
                                 font=font2)
                elif len(str(time_['duanwu'])) == 3:
                    Alltext.text(xy=(162, 248 + 25 + 25 + 26 + 26), text=str(time_['duanwu'])[2], fill=(255, 0, 0),
                                 font=font2)
                    Alltext.text(xy=(162 - 11, 248 + 25 + 25 + 26 + 26), text=str(time_['duanwu'])[1], fill=(255, 0, 0),
                                 font=font2)
                    Alltext.text(xy=(162 - 11 - 11, 248 + 25 + 25 + 26 + 26), text=str(time_['duanwu'])[0],
                                 fill=(255, 0, 0), font=font2)

                # 中秋节倒计时
                if len(str(time_['zhongqiu'])) == 1:
                    Alltext.text(xy=(162, 248 + 25 + 25 + 26 + 26 + 26), text=str(time_['zhongqiu']), fill=(255, 0, 0),
                                 font=font2)
                elif len(str(time_['zhongqiu'])) == 2:
                    Alltext.text(xy=(162, 248 + 25 + 25 + 26 + 26 + 26), text=str(time_['zhongqiu'])[1], fill=(255, 0, 0),
                                 font=font2)
                    Alltext.text(xy=(162 - 11, 248 + 25 + 25 + 26 + 26 + 26), text=str(time_['zhongqiu'])[0],
                                 fill=(255, 0, 0), font=font2)
                elif len(str(time_['zhongqiu'])) == 3:
                    Alltext.text(xy=(162, 248 + 25 + 25 + 26 + 26 + 26), text=str(time_['zhongqiu'])[2], fill=(255, 0, 0),
                                 font=font2)
                    Alltext.text(xy=(162 - 11, 248 + 25 + 25 + 26 + 26 + 26), text=str(time_['zhongqiu'])[1],
                                 fill=(255, 0, 0), font=font2)
                    Alltext.text(xy=(162 - 11 - 11, 248 + 25 + 25 + 26 + 26 + 26), text=str(time_['zhongqiu'])[0],
                                 fill=(255, 0, 0),
                                 font=font2)

                # 国庆节倒计时
                if len(str(time_['guoqing'])) == 1:
                    Alltext.text(xy=(162, 248 + 25 + 25 + 26 + 26 + 26 + 26), text=str(time_['guoqing']), fill=(255, 0, 0),
                                 font=font2)
                elif len(str(time_['guoqing'])) == 2:
                    Alltext.text(xy=(162, 248 + 25 + 25 + 26 + 26 + 26 + 26), text=str(time_['guoqing'])[1],
                                 fill=(255, 0, 0), font=font2)
                    Alltext.text(xy=(162 - 11, 248 + 25 + 25 + 26 + 26 + 26 + 26), text=str(time_['guoqing'])[0],
                                 fill=(255, 0, 0),
                                 font=font2)
                elif len(str(time_['guoqing'])) == 3:
                    Alltext.text(xy=(162, 248 + 25 + 25 + 26 + 26 + 26 + 26), text=str(time_['guoqing'])[2],
                                 fill=(255, 0, 0), font=font2)
                    Alltext.text(xy=(162 - 11, 248 + 25 + 25 + 26 + 26 + 26 + 26), text=str(time_['guoqing'])[1],
                                 fill=(255, 0, 0),
                                 font=font2)
                    Alltext.text(xy=(162 - 11 - 11, 248 + 25 + 25 + 26 + 26 + 26 + 26), text=str(time_['guoqing'])[0],
                                 fill=(255, 0, 0),
                                 font=font2)

                # 元旦节倒计时
                if len(str(time_['yuandan'])) == 1:
                    Alltext.text(xy=(162, 248 + 25 + 25 + 26 + 26 + 26 + 26 + 26), text=str(time_['yuandan']),
                                 fill=(255, 0, 0), font=font2)
                elif len(str(time_['yuandan'])) == 2:
                    Alltext.text(xy=(162, 248 + 25 + 25 + 26 + 26 + 26 + 26 + 26), text=str(time_['yuandan'])[1],
                                 fill=(255, 0, 0), font=font2)
                    Alltext.text(xy=(162 - 11, 248 + 25 + 25 + 26 + 26 + 26 + 26 + 26), text=str(time_['yuandan'])[0],
                                 fill=(255, 0, 0), font=font2)
                elif len(str(time_['yuandan'])) == 3:
                    Alltext.text(xy=(162, 248 + 25 + 25 + 26 + 26 + 26 + 26 + 26), text=str(time_['yuandan'])[2],
                                 fill=(255, 0, 0), font=font2)
                    Alltext.text(xy=(162 - 11, 248 + 25 + 25 + 26 + 26 + 26 + 26 + 26), text=str(time_['yuandan'])[1],
                                 fill=(255, 0, 0), font=font2)
                    Alltext.text(xy=(162 - 11 - 11, 248 + 25 + 25 + 26 + 26 + 26 + 26 + 26), text=str(time_['yuandan'])[0],
                                 fill=(255, 0, 0),
                                 font=font2)

                Image.Image.paste(bgimg, template, (0, 280))
                # shijianchuo = str(int(time.time()))
                bgimg.save(fp=savePath)


                # 以二进制模式读取文件
                with open(savePath, 'rb') as f:
                    filebytes = f.read()
                    # 发送最终效果图
                    if message["IsGroup"]:
                        await bot.send_image_message(message["FromWxid"], filebytes)
                    else:
                        await bot.send_image_message(message["SenderWxid"], filebytes)

                return False
        except Exception as e:
            logger.error(f"摸鱼功能出错: {e}")


    @schedule('cron', hour=5, minute=0, second=0)
    async def daily_task(self, bot: WechatAPIClient):
        if not self.enable:
            return
        target_dir = "plugins/Moyu/image"

        for root, _, files in os.walk(target_dir):
            for file in files:
                if file.lower().endswith(".png"):
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        logger.info(f"✅ 已删除摸鱼缓存图片: {file_path}")
                    except Exception as e:
                        logger.info(f"❌ 摸鱼缓存图片删除失败: {file_path} - {e}")
        return