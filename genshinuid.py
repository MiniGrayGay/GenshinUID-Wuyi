import base64
from pathlib import Path
import traceback

from aiocqhttp.exceptions import ActionFailed
from aiohttp import ClientConnectorError
from hoshino import Service
from hoshino.typing import CQEvent, HoshinoBot
from nonebot import MessageSegment, get_bot

from .mihoyo_libs.get_image import *
from .mihoyo_libs.get_mihoyo_bbs_data import *
from .enkaToData.enkaToData import *
from .enkaToData.drawCharCard import *

R_PATH = Path(__file__).parents[0]

sv = Service('Genshinuid')
hoshino_bot = get_bot()

FILE_PATH = os.path.join(os.path.join(os.path.dirname(__file__), 'mihoyo_libs'), 'mihoyo_bbs')
INDEX_PATH = os.path.join(FILE_PATH, 'index')
Texture_PATH = os.path.join(FILE_PATH, 'texture2d')

AUTO_REFRESH = False
CK_HINT = '''
获取Cookies教程请回复 绑定 查看。
提示：
绑定uid：uid为原神uid，如 绑定uid119379594
绑定mys：mys为米游社通行证，如 绑定mys197845456
绑定cookie：cookie是米游社账号的临时通信凭证，如：
绑定 account_id=197845456; cookie_token=tQcb0QFfA79TLZRx3rIKk9KhoVvIGv8Pggl5u36b'''

@sv.on_fullmatch('帮助|help')
async def send_help_pic(bot: HoshinoBot, ev: CQEvent):
    try:
        help_path = os.path.join(INDEX_PATH,'help.png')
        f = open(help_path, 'rb')
        ls_f = b64encode(f.read()).decode()
        img_mes = 'base64://' + ls_f
        f.close()
        await bot.send(ev, MessageSegment.image(img_mes))
    except Exception:
        logger.exception('获取帮助失败。')

@sv.on_prefix('毕业度统计')
async def send_charcard_list(bot: HoshinoBot, ev: CQEvent):
    message = ev.message.extract_plain_text()
    message = message.replace(' ', '')
    at = re.search(r'\[CQ:at,qq=(\d*)]', str(ev.message))
    limit = re.findall(r'\d+', message)  # str
    if len(limit) >= 1:
        limit = int(limit[0])
    else:
        limit = 32
    if at:
        at = at.group(1)
        uid = await select_db(at, mode='uid')
        message = message.replace(str(at), '')
    else:
        uid = await select_db(int(ev.sender['user_id']), mode='uid')
    uid = uid[0]
    im = await draw_cahrcard_list(uid, limit)

    if im.startswith('base64://'):
        await bot.send(ev, MessageSegment.image(im))
    else:
        await bot.send(ev, str(im))
    logger.info(f'UID{uid}获取角色数据成功！')

@sv.on_rex('[\u4e00-\u9fa5]+(推荐)')
async def send_guide_pic(bot: HoshinoBot, ev: CQEvent):
    try:
        message = str(ev.message).strip().replace(' ', '')[:-2]
        with open(os.path.join(INDEX_PATH,'char_alias.json'),'r',encoding='utf8')as fp:
            char_data = json.load(fp)
        name = message
        for i in char_data:
            if message in i:
                name = i
            else:
                for k in char_data[i]:
                    if message in k:
                        name = i
        #name = str(event.get_message()).strip().replace(' ', '')[:-2]
        url = 'https://img.genshin.minigg.cn/guide/{}.jpg'.format(name)
        if httpx.head(url).status_code == 200:
            await bot.send(ev, MessageSegment.image(url))
        else:
            return
    except Exception:
        logger.exception('获取建议失败。')

@sv.on_rex('[\u4e00-\u9fa5]+(用什么|能用啥|怎么养)')
async def send_char_adv(bot: HoshinoBot, ev: CQEvent):
    try:
        name = str(ev.message).strip().replace(' ', '')[:-3]
        im = await char_adv(name)
        await bot.send(ev, im)
    except Exception:
        logger.exception('获取建议失败。')


@sv.on_rex('[\u4e00-\u9fa5]+(能给谁|给谁用|要给谁|谁能用)')
async def send_weapon_adv(bot: HoshinoBot, ev: CQEvent):
    try:
        name = str(ev.message).strip().replace(' ', '')[:-3]
        im = await weapon_adv(name)
        await bot.send(ev, im)
    except Exception:
        logger.exception('获取建议失败。')

@sv.on_prefix('绑定 ')#自己加的，群内绑定消息验证
async def send_addck(bot: HoshinoBot, ev: CQEvent):
    text = ev.message.extract_plain_text().strip()
    try:
        await bot.delete_msg(self_id=ev.self_id, message_id=ev.message_id)
    except:
        await bot.send(ev, "正在验证中，请主动撤回该消息")
    try:
        mes = text
        im = await deal_ck(mes, ev.user_id)
        await bot.send(ev, im)
    except ActionFailed as e:
        await bot.send(ev,'机器人发送消息失败：{}'.format(e))
        logger.exception('发送Cookie校验信息失败')
    except Exception as e:
        await bot.send(ev,'校验失败！请输入正确的Cookies！\n错误信息为{}'.format(e))
        logger.exception('Cookie校验失败')

@sv.on_prefix('收益曲线')
async def send_blue_pic(bot: HoshinoBot, ev: CQEvent):
    pic_json = {'帮助':'https://img.nga.178.com/attachments/mon_202208/21/i2Qjk1-j5voXxZ96T3cS1di-q9.png',
                '说明':'https://img.nga.178.com/attachments/mon_202208/21/i2Qjk1-j5voXxZ96T3cS1di-q9.png',
                '安柏':'https://img.nga.178.com/attachments/mon_202208/17/i2Q2q-8m6vXxZ91T3cS1di-q9.png',
                '班尼特':'https://img.nga.178.com/attachments/mon_202208/17/i2Q2q-i6w3XwZ8xT3cS1di-q9.png',
                '迪卢克':'https://img.nga.178.com/attachments/mon_202208/17/i2Q2q-dgbbXxZ92T3cS1di-q9.png',
                '胡桃':'https://img.nga.178.com/attachments/mon_202208/17/i2Q2q-6vbsXvZ8pT3cS1di-q9.png',
                '可莉':'https://img.nga.178.com/attachments/mon_202208/17/i2Q2q-bplpXwZ8zT3cS1di-q9.png',
                '托马':'https://img.nga.178.com/attachments/mon_202208/17/i2Q2q-in5cXwZ90T3cS1di-q9.png',
                '香菱':'https://img.nga.178.com/attachments/mon_202208/17/i2Q2q-akwxXwZ8wT3cS1di-q9.png',
                '宵宫':'https://img.nga.178.com/attachments/mon_202208/17/i2Q2q-acsfXyZ9eT3cS1di-q9.png',
                '辛焱':'https://img.nga.178.com/attachments/mon_202208/17/i2Q2q-1uboXyZ9cT3cS1di-q9.png',
                '烟绯':'https://img.nga.178.com/attachments/mon_202208/17/i2Q2q-gz71XxZ96T3cS1di-q9.png',
                '妮露':'https://img.nga.178.com/attachments/mon_202302/07/i2Q180-7njbXuZ8aT3cS1di-q9.png',
                '芭芭拉':'https://img.nga.178.com/attachments/mon_202208/17/i2Q2q-1t4oXxZ95T3cS1di-q9.png',
                '达达利亚':'https://img.nga.178.com/attachments/mon_202208/17/i2Q2q-hu24XyZ9cT3cS1di-q9.png',
                '莫娜':'https://img.nga.178.com/attachments/mon_202208/17/i2Q2q-9cifXyZ9bT3cS1di-q9.png',
                '珊瑚宫心海':'https://img.nga.178.com/attachments/mon_202208/17/i2Q2q-3ktjXxZ9bT3cS1di-q9.png',
                '神里绫人':'https://img.nga.178.com/attachments/mon_202208/17/i2Q2q-hyagXyZ9fT3cS1di-q9.png',
                '行秋':'https://img.nga.178.com/attachments/mon_202208/17/i2Q2q-b18cXwZ91T3cS1di-q9.png',
                '夜兰':'https://img.nga.178.com/attachments/mon_202208/17/i2Q2q-3oq4XxZ95T3cS1di-q9.png',
                '流浪者':'https://img.nga.178.com/attachments/mon_202302/07/i2Q180-71e3XtZ87T3cS1di-q9.png',
                '珐露珊':'https://img.nga.178.com/attachments/mon_202302/07/i2Q180-cf75XuZ87T3cS1di-q9.png',
                '枫原万叶':'https://img.nga.178.com/attachments/mon_202208/24/i2Q8oyf-i5niXvZ8iT3cS1di-q9.png',
                '鹿野院平藏':'https://img.nga.178.com/attachments/mon_202208/21/i2Qjk1-jx1yXxZ92T3cS1di-q9.png',
                '旅行者风':'https://img.nga.178.com/attachments/mon_202208/24/i2Q8oyf-bplhXvZ8lT3cS1di-q9.png',
                '琴':'https://img.nga.178.com/attachments/mon_202208/21/i2Qjk1-kqstXxZ9aT3cS1di-q9.png',
                '砂糖':'https://img.nga.178.com/attachments/mon_202208/24/i2Q8oyf-95mbXwZ8vT3cS1di-q9.png',
                '温迪':'https://img.nga.178.com/attachments/mon_202208/24/i2Q8oyf-2s69XwZ8uT3cS1di-q9.png',
                '魈':'https://img.nga.178.com/attachments/mon_202208/21/i2Qjk1-htbXwZ8yT3cS1di-q9.png',
                '早柚':'https://img.nga.178.com/attachments/mon_202208/21/i2Qjk1-28j7XxZ94T3cS1di-q9.png',
                '艾尔海森':'https://img.nga.178.com/attachments/mon_202302/07/i2Q180-4ntzXuZ8fT3cS1di-q9.png',
                '瑶瑶':'https://img.nga.178.com/attachments/mon_202302/07/i2Q180-a6gvXtZ82T3cS1di-q9.png',
                '纳西妲':'https://img.nga.178.com/attachments/mon_202302/07/i2Q180-klw9Z2pT3cS1di-q9.png',
                '柯莱':'https://img.nga.178.com/attachments/mon_202208/24/i2Q8oyf-86c8XvZ8pT3cS1di-q9.png',
                '旅行者草':'https://img.nga.178.com/attachments/mon_202208/24/i2Q8oyf-620hXuZ8aT3cS1di-q9.png',
                '提纳里':'https://img.nga.178.com/attachments/mon_202208/24/i2Q8oyf-1twzXwZ8uT3cS1di-q9.png',
                '赛诺':'https://img.nga.178.com/attachments/mon_202302/07/i2Q180-i3a5X10Z9vT3cS1di-q9.png',
                '八重神子':'https://img.nga.178.com/attachments/mon_202208/24/i2Q8oyf-ddaeXyZ9kT3cS1di-q9.png',
                '北斗':'https://img.nga.178.com/attachments/mon_202208/24/i2Q8oyf-5xbkZ2dT3cS1di-q9.png',
                '多莉':'https://img.nga.178.com/attachments/mon_202209/09/i2Q181-45azXyZ9bT3cS1di-q9.png',
                '菲谢尔':'https://img.nga.178.com/attachments/mon_202208/24/i2Q8oyf-77grXxZ98T3cS1di-q9.png',
                '九条裟罗':'https://img.nga.178.com/attachments/mon_202208/21/i2Qjk1-ep0dXwZ8yT3cS1di-q9.png',
                '久岐忍':'https://img.nga.178.com/attachments/mon_202208/24/i2Q8oyf-1zzuXxZ97T3cS1di-q9.png',
                '刻晴':'https://img.nga.178.com/attachments/mon_202208/24/i2Q8oyf-j403XyZ9hT3cS1di-q9.png',
                '雷电将军':'https://img.nga.178.com/attachments/mon_202303/05/i2Qjr7-kszoXyZ9eT3cS1di-q9.png',
                '雷电将军2':'https://img.nga.178.com/attachments/mon_202303/05/i2Qjr7-ei3cXyZ9fT3cS1di-q9.png',
                '雷泽':'https://img.nga.178.com/attachments/mon_202208/21/i2Qjk1-axdiXxZ97T3cS1di-q9.png',
                '丽莎':'https://img.nga.178.com/attachments/mon_202208/24/i2Q8oyf-ba0sXxZ96T3cS1di-q9.png',
                '旅行者雷':'https://img.nga.178.com/attachments/mon_202208/21/i2Qjk1-aqakXxZ93T3cS1di-q9.png',
                '莱依拉':'https://img.nga.178.com/attachments/mon_202302/07/i2Q180-p52XuZ8bT3cS1di-q9.png',
                '埃洛伊':'https://img.nga.178.com/attachments/mon_202208/19/i2Q2q-a90bXwZ8yT3cS1di-q9.png',
                '迪奥娜':'https://img.nga.178.com/attachments/mon_202208/19/i2Q2q-4pvvXxZ97T3cS1di-q9.png',
                '甘雨':'https://img.nga.178.com/attachments/mon_202208/19/i2Q2q-jh27XxZ96T3cS1di-q9.png',
                '凯亚':'https://img.nga.178.com/attachments/mon_202208/19/i2Q2q-cpsdXxZ96T3cS1di-q9.png',
                '罗莎莉亚':'https://img.nga.178.com/attachments/mon_202208/19/i2Q2q-2tppXyZ9cT3cS1di-q9.png',
                '七七':'https://img.nga.178.com/attachments/mon_202208/19/i2Q2q-gbmkXxZ99T3cS1di-q9.png',
                '申鹤':'https://img.nga.178.com/attachments/mon_202208/19/i2Q2q-2mawXxZ9bT3cS1di-q9.png',
                '神里绫华':'https://img.nga.178.com/attachments/mon_202208/19/i2Q2q-jurwXxZ97T3cS1di-q9.png',
                '优菈':'https://img.nga.178.com/attachments/mon_202208/19/i2Q2q-ec2aXxZ98T3cS1di-q9.png',
                '重云':'https://img.nga.178.com/attachments/mon_202208/19/i2Q2q-al2oXxZ9bT3cS1di-q9.png',
                '阿贝多':'https://img.nga.178.com/attachments/mon_202208/19/i2Q2q-cwmhXwZ8wT3cS1di-q9.png',
                '荒泷一斗':'https://img.nga.178.com/attachments/mon_202208/19/i2Q2q-73zhXxZ97T3cS1di-q9.png',
                '旅行者岩':'https://img.nga.178.com/attachments/mon_202208/19/i2Q2q-kje0XxZ92T3cS1di-q9.png',
                '凝光':'https://img.nga.178.com/attachments/mon_202208/19/i2Q2q-3sa1XxZ94T3cS1di-q9.png',
                '诺艾尔':'https://img.nga.178.com/attachments/mon_202208/19/i2Q2q-9ht1XxZ97T3cS1di-q9.png',
                '五郎':'https://img.nga.178.com/attachments/mon_202208/19/i2Q2q-j6rfXxZ9aT3cS1di-q9.png',
                '云堇':'https://img.nga.178.com/attachments/mon_202208/19/i2Q2q-9yzvXxZ97T3cS1di-q9.png',
                '钟离':'https://img.nga.178.com/attachments/mon_202208/19/i2Q2q-3ifiXwZ8zT3cS1di-q9.png'}
    try:
        message = ev.message.extract_plain_text().replace(' ', '')
        await bot.send(ev, MessageSegment.image(pic_json[message]))
    except:
        await bot.send(ev, '请输入角色的官方名称，如果还是不出来说明没有这个角色的收益曲线')


@sv.on_prefix('参考面板')
async def send_bluekun_pic(bot: HoshinoBot, ev: CQEvent):
    pic_json = {'雷':'https://upload-bbs.miyoushe.com/upload/2023/01/18/160367110/89fdd33dfca1f94b8dc7ed177f7cf450_5412131885124736072.jpg',
                '火':'https://upload-bbs.miyoushe.com/upload/2023/01/18/160367110/b3f9f9cb3a0a1dc3a0f9fb6f7fc7affc_3254062406051995278.jpg',
                '冰':'https://upload-bbs.miyoushe.com/upload/2023/01/18/160367110/8d923389e9d1a6f6099567a9ef2f8ab8_8261213444812001201.jpg',
                '风':'https://upload-bbs.miyoushe.com/upload/2023/01/18/160367110/600fdf566eed198b2afa4aa17abcf9b9_1453750001943981356.jpg',
                '水':'https://upload-bbs.miyoushe.com/upload/2023/01/18/160367110/2a0b051f9b8d304d341592764ff3eb70_8478428213254812413.jpg',
                '岩':'https://upload-bbs.miyoushe.com/upload/2023/01/18/160367110/495dc0b51a37482299fd472352a6eec4_6596047289346261223.jpg',
                '草':'https://upload-bbs.miyoushe.com/upload/2023/01/18/160367110/050f782133d8e95fea42f846d7f26f5d_277093892361893116.png'}
    try:
        message = ev.message.extract_plain_text().replace(' ', '')
        await bot.send(ev, MessageSegment.image(pic_json[message]))
    except:
        await bot.send(ev, '请输入元素属性，如：参考面板 风')

@sv.on_prefix('语音')
async def send_audio(bot: HoshinoBot, ev: CQEvent):
    try:
        message = ev.message.extract_plain_text()
        message = message.replace(' ', '')
        name = ''.join(re.findall('[\u4e00-\u9fa5]', message))
        im = await audio_wiki(name, message)
        if name == '列表':
            ls_f = base64.b64encode(im).decode()
            img = 'base64://' + ls_f
            await bot.send(ev, MessageSegment.image(img))
        else:
            audios = 'base64://' + b64encode(im).decode()
            await bot.send(ev, MessageSegment.record(audios))
    except ActionFailed as e:
        logger.exception('获取语音失败')
        # await bot.send(ev, '机器人发送消息失败：{}'.format(e))
    except Exception as e:
        logger.exception('获取语音失败或ffmpeg未配置')
        # await bot.send(ev, '发生错误 {},请检查后台输出。'.format(e))

@sv.on_fullmatch('活动列表')
async def send_polar(bot: HoshinoBot, ev: CQEvent):
    try:
        img_path = os.path.join(FILE_PATH, 'event.jpg')
        while 1:
            if os.path.exists(img_path):
                f = open(img_path, 'rb')
                ls_f = base64.b64encode(f.read()).decode()
                img_mihoyo_bbs = 'base64://' + ls_f
                f.close()
                break
            else:
                await draw_event_pic()
        await bot.send(ev, MessageSegment.image(img_mihoyo_bbs))
    except ActionFailed as e:
        # await bot.send(ev, '机器人发送消息失败：{}'.format(e))
        logger.exception('发送活动列表失败')
    except Exception as e:
        # await bot.send(ev, '发生错误 {},请检查后台输出。'.format(e))
        logger.exception('获取活动列表错误')


@sv.on_fullmatch('御神签')
async def send_lots(bot: HoshinoBot, ev: CQEvent):
    try:
        qid = ev.sender['user_id']
        raw_data = await get_a_lots(qid)
        im = base64.b64decode(raw_data).decode('utf-8')
        await bot.send(ev, im)
    except ActionFailed as e:
        # await bot.send(ev, '机器人发送消息失败：{}'.format(e))
        logger.exception('发送御神签失败')
    except Exception as e:
        # await bot.send(ev, '发生错误 {},请检查后台输出。'.format(e))
        logger.exception('获取御神签错误')


@sv.on_prefix('材料')
async def send_cost(bot: HoshinoBot, ev: CQEvent):
    try:
        message = ev.message.extract_plain_text()
        message = message.replace(' ', '')
        im = await char_wiki(message, 'costs')
        await bot.send(ev, im)
    except ActionFailed as e:
        # await bot.send(ev, '机器人发送消息失败：{}'.format(e))
        logger.exception('发送材料信息失败')
    except Exception as e:
        # await bot.send(ev, '发生错误 {},请检查后台输出。'.format(e))
        logger.exception('获取材料信息错误')


@sv.on_prefix('原魔')
async def send_enemies(bot: HoshinoBot, ev: CQEvent):
    try:
        message = ev.message.extract_plain_text()
        im = await enemies_wiki(message)
        await bot.send(ev, im)
    except ActionFailed as e:
        # await bot.send(ev, '机器人发送消息失败：{}'.format(e))
        logger.exception('发送怪物信息失败')
    except Exception as e:
        # await bot.send(ev, '发生错误 {},请检查后台输出。'.format(e))
        logger.exception('获取怪物信息错误')


@sv.on_prefix('食物')
async def send_food(bot: HoshinoBot, ev: CQEvent):
    try:
        message = ev.message.extract_plain_text()
        im = await foods_wiki(message)
        await bot.send(ev, im)
    except ActionFailed as e:
        # await bot.send(ev, '机器人发送消息失败：{}'.format(e))
        logger.exception('发送食物信息失败')
    except Exception as e:
        # await bot.send(ev, '发生错误 {},请检查后台输出。'.format(e))
        logger.exception('获取食物信息错误')


@sv.on_prefix('圣遗物')
async def send_artifacts(bot: HoshinoBot, ev: CQEvent):
    try:
        message = ev.message.extract_plain_text()
        im = await artifacts_wiki(message)

        if im != '该圣遗物不存在。':
            await bot.send(ev, im)
    except ActionFailed as e:
        # await bot.send(ev, '机器人发送消息失败：{}'.format(e))
        logger.exception('发送圣遗物信息失败')
    except Exception as e:
        # await bot.send(ev, '发生错误 {},请检查后台输出。'.format(e))
        logger.exception('获取圣遗物信息错误')


@sv.on_prefix('天赋')
async def send_talents(bot: HoshinoBot, ev: CQEvent):
    try:
        message = ev.message.extract_plain_text()
        name = ''.join(re.findall('[\u4e00-\u9fa5]', message))
        num = re.findall(r'[0-9]+', message)
        if len(num) == 1:
            im = await char_wiki(name, 'talents', num[0])
            if isinstance(im, list):
                await hoshino_bot.send_group_forward_msg(group_id=ev.group_id, messages=im)
                return
        else:
            im = '参数不正确。'
        await bot.send(ev, im)
    except ActionFailed as e:
        # await bot.send(ev, '机器人发送消息失败：{}'.format(e))
        logger.exception('发送天赋信息失败')
    except Exception as e:
        # await bot.send(ev, '发生错误 {},请检查后台输出。'.format(e))
        logger.exception('获取天赋信息错误')


@sv.on_prefix('武器')
async def send_weapon(bot: HoshinoBot, ev: CQEvent):
    try:
        message = ev.message.extract_plain_text()
        name = ''.join(re.findall('[\u4e00-\u9fa5]', message))
        level = re.findall(r'[0-9]+', message)
        if len(level) == 1:
            im = await weapon_wiki(name, level=level[0])
        else:
            im = await weapon_wiki(name)
        if im != '该武器不存在。':
            await bot.send(ev, im, at_sender=True)
    except ActionFailed as e:
        # await bot.send(ev, '机器人发送消息失败：{}'.format(e))
        logger.exception('发送武器信息失败')
    except Exception as e:
        # await bot.send(ev, '发生错误 {},请检查后台输出。'.format(e))
        logger.exception('获取武器信息错误')


@sv.on_prefix('角色')
async def send_char(bot: HoshinoBot, ev: CQEvent):
    try:
        message = ev.message.extract_plain_text()
        message = message.replace(' ', '')
        name = ''.join(re.findall('[\u4e00-\u9fa5]', message))
        level = re.findall(r'[0-9]+', message)
        if len(level) == 1:
            im = await char_wiki(name, 'char', level=level[0])
        else:
            im = await char_wiki(name)
        if im != '不存在该角色或类型。':
            await bot.send(ev, im)
    except ActionFailed as e:
        # await bot.send(ev, '机器人发送消息失败：{}'.format(e))
        logger.exception('发送角色信息失败')
    except Exception as e:
        # await bot.send(ev, '发生错误 {},请检查后台输出。'.format(e))
        logger.exception('获取角色信息错误')


@sv.on_prefix('命座')
async def send_polar(bot: HoshinoBot, ev: CQEvent):
    try:
        message = ev.message.extract_plain_text()
        num = int(re.findall(r'\d+', message)[0])  # str
        m = ''.join(re.findall('[\u4e00-\u9fa5]', message))
        if num <= 0 or num > 6:
            await bot.send(ev, '角色{}不存在或命座{}不存在'.format(m, num), at_sender=True)
        else:
            im = await char_wiki(m, 'constellations', num)
            await bot.send(ev, im, at_sender=True)
    except ActionFailed as e:
        # await bot.send(ev, '机器人发送消息失败：{}'.format(e))
        logger.exception('发送命座信息失败')
    except Exception as e:
        # await bot.send(ev, '发生错误 {},请检查后台输出。'.format(e))
        logger.exception('获取命座信息错误')


# 每日零点清空cookies使用缓存
@sv.scheduled_job('cron', hour='0')
async def clean_cache():
    await delete_cache()


@sv.scheduled_job('cron', hour='1')
async def draw_event():
    await draw_event_pic()

@sv.scheduled_job('cron', hour='2')
async def daily_refresh_charData():
    global AUTO_REFRESH
    if AUTO_REFRESH:
        await refresh_charData()

async def refresh_charData():
    conn = sqlite3.connect('ID_DATA.db')
    c = conn.cursor()
    cursor = c.execute('SELECT UID  FROM UIDDATA WHERE UID IS NOT NULL')
    c_data = cursor.fetchall()
    t = 0
    for row in c_data:
        uid = row[0]
        try:
            im = await enkaToData(uid)
            logger.info(im)
            t += 1
            await asyncio.sleep(18 + random.randint(2, 6))
        except:
            logger.exception(f'{uid}刷新失败！')
            logger.error(f'{uid}刷新失败！本次自动刷新结束！')
            return f'执行失败从{uid}！共刷新{str(t)}个角色！'
    else:
        return f'执行成功！共刷新{str(t)}个角色！'
    
# @sv.on_prefix('强制刷新')
# async def send_card_info(bot: HoshinoBot, ev: CQEvent):
    # message = ev.message.extract_plain_text()
    # uid = re.findall(r'\d+', message)  # str
    # m = ''.join(re.findall('[\u4e00-\u9fa5]', message))
    # qid = str(ev.sender['user_id'])
    # try:
        # if len(uid) >= 1:
            # uid = uid[0]
        # else:
            # if m == '全部数据':
                # if qid in bot.config.SUPERUSERS:
                    # await bot.send(ev, '开始刷新全部数据，这可能需要相当长的一段时间！！')
                    # im = await refresh_charData()
                    # await bot.send(ev, str(im))
                    # return
                # else:
                    # return
            # else:
                # uid = await select_db(qid, mode='uid')
                # uid = uid[0]
        # im = await enkaToData(uid)
        # await bot.send(ev, str(im))
        # logger.info(f'UID{uid}获取角色数据成功！')
    # except:
        # await bot.send(ev, '获取角色数据失败！')
        # logger.exception('获取角色数据失败！')

# @sv.on_fullmatch('开始获取米游币') #为防止米游币程序崩溃，已关闭手动获取
# async def send_mihoyo_coin(bot: HoshinoBot, ev: CQEvent):
    # await bot.send(ev, '开始操作……', at_sender=True)
    # try:
        # qid = ev.sender['user_id']
        # im_mes = await mihoyo_coin(int(qid))
        # im = im_mes
    # except TypeError or AttributeError:
        # im = '没有找到绑定信息。\n' + CK_HINT
        # logger.exception('获取米游币失败')
    # except Exception as e:
        # im = '芭比Q了，你的操作导致米游币程序发生错误 {},也许是上一个用户的米游币任务还未完成。请等待操作完成。'.format(e)
        # logger.exception('获取米游币失败')
    # finally:
        # try:
            # await bot.send(ev, im, at_sender=True)
        # except ActionFailed as e:
            # await bot.send(ev, '机器人发送消息失败：{}'.format(e.info['wording']))
            # logger.exception('发送签到信息失败')


@sv.on_fullmatch('全部重签')
async def _(bot: HoshinoBot, ev: CQEvent):
    try:
        if ev.user_id not in bot.config.SUPERUSERS:
            return
        await bot.send(ev, '已开始执行')
        await daily_sign()
    except ActionFailed as e:
        await bot.send(ev, '机器人发送消息失败：{}'.format(e))
    except Exception as e:
        traceback.print_exc()
        await bot.send(ev, '发生错误 {},请检查后台输出。'.format(e))


@sv.on_fullmatch('全部重获取')
async def bbscoin_resign(bot: HoshinoBot, ev: CQEvent):
    try:
        if ev.user_id not in bot.config.SUPERUSERS:
            return
        await bot.send(ev, '已开始执行')
        await daily_mihoyo_bbs_sign()
    except ActionFailed as e:
        await bot.send(ev, '机器人发送消息失败：{}'.format(e))
    except Exception as e:
        traceback.print_exc()
        await bot.send(ev, '发生错误 {},请检查后台输出。'.format(e))


# # 每隔半小时检测树脂是否超过设定值
# @sv.scheduled_job('cron', minute='*/30')
# async def push():
    # daily_data = await daily()
    # if daily_data is not None:
        # for i in daily_data:
            # if i['gid'] == 'on':
                # await hoshino_bot.send_private_msg(user_id=i['qid'], message=i['message'])
            # else:
                # await hoshino_bot.send_group_msg(group_id=i['gid'], message=f'[CQ:at,qq={i["qid"]}]'
                                                                            # + '\n' + i['message'])
    # else:
        # pass


# 每日零点1分进行米游社签到
@sv.scheduled_job('cron', hour='0', minute='1')
async def daily_sign_schedule():
    await daily_sign()


async def daily_sign():
    conn = sqlite3.connect('ID_DATA.db')
    c = conn.cursor()
    cursor = c.execute(
        'SELECT *  FROM NewCookiesTable WHERE StatusB != ?', ('off',))
    c_data = cursor.fetchall()
    temp_list = []
    for row in c_data:
        im = await sign(str(row[0]))
        if row[4] == 'on':
            try:
                await hoshino_bot.send_private_msg(user_id=row[2], message=im)
            except:
                logger.exception(f'{im} Error')
        else:
            message = f'[CQ:at,qq={row[2]}]\n{im}'
            if await config_check('SignReportSimple'):
                for i in temp_list:
                    if row[4] == i['push_group']:
                        if im == '签到失败，您未绑定过uid/cookie,或是绑定的cookie失效。请先发送 绑定 ，按照教程在群内绑定你的账号信息。' or im.startswith('网络有点忙，请稍后再试~!'):
                            i['failed'] += 1
                            i['push_message'] += '\n' + message
                        else:
                            i['success'] += 1
                        break
                else:
                    if im == '签到失败，您未绑定过uid/cookie,或是绑定的cookie失效。请先发送 绑定 ，按照教程在群内绑定你的账号信息。':
                        temp_list.append({'push_group': row[4], 'push_message': message, 'success': 0, 'failed': 1})
                    else:
                        temp_list.append({'push_group': row[4], 'push_message': '', 'success': 1, 'failed': 0})
            else:
                for i in temp_list:
                    if row[4] == i['push_group'] and i['num'] < 4:
                        i['push_message'] += '\n' + message
                        i['num'] += 1
                        break
                else:
                    temp_list.append({'push_group': row[4], 'push_message': message, 'num': 1})
        await asyncio.sleep(6 + random.randint(1, 3))
    if await config_check('SignReportSimple'):
        for i in temp_list:
            try:
                report = '以下为签到失败报告：{}'.format(i['push_message']) if i['push_message'] != '' else ''
                await hoshino_bot.send_group_msg(group_id=i['push_group'],
                                                 message='今日自动签到已完成！\n本群共签到成功{}人，'
                                                         '共签到失败{}人。{}'.format(i['success'], i['failed'], report))
            except:
                logger.exception('签到报告发送失败：{}'.format(i['push_message']))
            await asyncio.sleep(4 + random.randint(1, 3))
    else:
        for i in temp_list:
            try:
                await hoshino_bot.send_group_msg(group_id=i['push_group'], message=i['push_message'])
            except:
                logger.exception('签到报告发送失败：{}'.format(i['push_message']))
            await asyncio.sleep(4 + random.randint(1, 3))
    conn.close()
    return


# 每日三点二十五进行米游币获取，因为用时较长，三点重启电脑，大概需要十五分钟上传备份文件，米游币则在三点二十五分钟开始
@sv.scheduled_job('cron', hour='3', minute='25')
async def sign_at_night():
    await daily_mihoyo_bbs_sign()


async def daily_mihoyo_bbs_sign():
    conn = sqlite3.connect('ID_DATA.db')
    c = conn.cursor()
    cursor = c.execute(
        'SELECT *  FROM NewCookiesTable WHERE StatusC != ?', ('off',))
    c_data = cursor.fetchall()
    im_success = 0
    im_failed = 0
    im_failed_str = ''
    for row in c_data:
        logger.info('正在执行{}'.format(row[0]))
        if row[8]:
            await asyncio.sleep(5 + random.randint(1, 3))
            im = await mihoyo_coin(str(row[2]), str(row[8]))
            try:
                logger.info('已执行完毕：{}'.format(row[0]))
                im_success += 1
                if await config_check('MhyBBSCoinReport'):
                    await hoshino_bot.send_private_msg(user_id=row[2], message=im)
            except Exception:
                logger.exception('执行失败：{}'.format(row[0]))
                im_failed += 1
                im_failed_str += '\n' + '执行失败：{}'.format(row[0])
    faild_im = '\n以下为签到失败报告：{}'.format(im_failed_str) if im_failed_str != '' else ''
    im = '今日获取米游币成功的用户数量：{}，失败数量：{}{}'.format(im_success, im_failed, faild_im)
    for qid in hoshino_bot.config.SUPERADMIN:
        await hoshino_bot.send_private_msg(user_id = qid, message = im)
        await asyncio.sleep(5 + random.randint(1, 3))
    logger.info('已结束。')


# 私聊事件-为防风控冻结，改群聊了
@hoshino_bot.on_message('group')
async def setting(ctx):
    message = ctx['raw_message']
    sid = int(ctx['self_id'])
    userid = int(ctx['sender']['user_id'])
    gid = int(ctx['group_id'])
    # gid = 0
    # if '添加 ' in message:
        # try:
            # mes = message.replace('添加 ', '')
            # im = await deal_ck(mes, userid)
            # await hoshino_bot.send_msg(self_id=sid, user_id=userid, group_id=gid,
                                       # message=im)
        # except ActionFailed as e:
            # await hoshino_bot.send_msg(self_id=sid, user_id=userid, group_id=gid,
                                       # message='机器人发送消息失败：{}'.format(e))
            # logger.exception('发送Cookie校验信息失败')
        # except Exception as e:
            # await hoshino_bot.send_msg(self_id=sid, user_id=userid, group_id=gid,
                                       # message='校验失败！请输入正确的Cookies！\n错误信息为{}'.format(e))
            # logger.exception('Cookie校验失败')
    if '开启推送' in message:
        try:
            uid = await select_db(userid, mode='uid')
            im = await open_push(int(uid[0]), userid, 'off', 'StatusA')
            await hoshino_bot.send_group_msg(group_id=gid, message=im)
        except ActionFailed as e:
            await hoshino_bot.send_group_msg(group_id=gid,
                                       message='机器人发送消息失败：{}'.format(e))
            logger.exception('私聊）发送开启推送信息失败')
        except Exception:
            await hoshino_bot.send_group_msg(group_id=gid, message='未找到绑定记录！\n' + CK_HINT)
            logger.exception('开启推送失败')
    elif '关闭推送' in message:
        try:
            uid = await select_db(userid, mode='uid')
            im = await open_push(int(uid[0]), userid, 'off', 'StatusA')
            await hoshino_bot.send_group_msg(group_id=gid, message=im)
        except ActionFailed as e:
            await hoshino_bot.send_group_msg(group_id=gid,
                                       message='机器人发送消息失败：{}'.format(e))
            logger.exception('私聊）发送关闭推送信息失败')
        except Exception:
            await hoshino_bot.send_group_msg(group_id=gid, message='未找到绑定记录！\n' + CK_HINT)
            logger.exception('关闭推送失败')
    elif '开启自动米游币' in message:
        try:
            uid = await select_db(userid, mode='uid')
            im = await open_push(int(uid[0]), userid, 'on', 'StatusC')
            await hoshino_bot.send_group_msg(group_id=gid,
                                       message=im, at_sender=True)
        except Exception:
            await hoshino_bot.send_group_msg(group_id=gid,
                                       message='未绑定uid信息！请先在群内绑定你的游戏uid，如：绑定uid119379594', at_sender=True)
    elif '关闭自动米游币' in message:
        try:
            uid = await select_db(userid, mode='uid')
            im = await open_push(int(uid[0]), userid, 'off', 'StatusC')
            await hoshino_bot.send_group_msg(group_id=gid,
                                       message=im, at_sender=True)
        except Exception:
            await hoshino_bot.send_group_msg(group_id=gid,
                                       message='未绑定uid信息！请先在群内绑定你的游戏uid，如：绑定uid119379594', at_sender=True)
    elif '开启自动签到' in message:
        try:
            uid = await select_db(userid, mode='uid')
            im = await open_push(int(uid[0]), userid, '340595850', 'StatusB')
            await hoshino_bot.send_group_msg(group_id=gid, message=im)
        except ActionFailed as e:
            await hoshino_bot.send_group_msg(group_id=gid,
                                       message='机器人发送消息失败：{}'.format(e))
            logger.exception('私聊）发送开启自动签到信息失败')
        except Exception:
            traceback.print_exc()
            await hoshino_bot.send_group_msg(group_id=gid, message='未找到绑定记录！\n' + CK_HINT)
            logger.exception('开启自动签到失败')
    elif '关闭自动签到' in message:
        try:
            uid = await select_db(userid, mode='uid')
            im = await open_push(int(uid[0]), userid, 'off', 'StatusA')
            await hoshino_bot.send_group_msg(group_id=gid, message=im)
        except ActionFailed as e:
            await hoshino_bot.send_group_msg(group_id=gid,
                                       message='机器人发送消息失败：{}'.format(e))
            logger.exception('私聊）发送关闭自动签到信息失败')
        except Exception:
            traceback.print_exc()
            await hoshino_bot.send_group_msg(group_id=gid, message='未找到绑定记录！\n' + CK_HINT)
            logger.exception('关闭自动签到失败')


# 群聊开启 自动签到 和 推送树脂提醒 功能
@sv.on_prefix('开启')
async def open_switch_func(bot: HoshinoBot, ev: CQEvent):
    try:
        at = re.search(r'\[CQ:at,qq=(\d*)]', str(ev.message))
        message = ev.message.extract_plain_text()
        m = ''.join(re.findall('[\u4e00-\u9fa5]', message))

        qid = ev.sender['user_id']

        if m == '自动签到':
            try:
                if at:
                    if qid in bot.config.SUPERUSERS:
                        qid = at.group(1)
                    else:
                        await bot.send(ev, '你没有权限。', at_sender=True)
                        return
                else:
                    qid = ev.sender['user_id']
                gid = ev.group_id
                uid = await select_db(qid, mode='uid')
                im = await open_push(int(uid[0]), ev.sender['user_id'], str(gid), 'StatusB')
                await bot.send(ev, im, at_sender=True)
            except ActionFailed as e:
                await bot.send(ev, '机器人发送消息失败：{}'.format(e))
                logger.exception('发送开启自动签到信息失败')
            except Exception:
                await bot.send(ev, '未绑定uid信息！请先在群内绑定你的游戏uid，如：绑定uid119379594', at_sender=True)
                logger.exception('开启自动签到失败')
        # elif m == '推送':
            # try:
                # if at:
                    # if qid in bot.config.SUPERUSERS:
                        # qid = at.group(1)
                    # else:
                        # await bot.send(ev, '你没有权限。', at_sender=True)
                        # return
                # else:
                    # qid = ev.sender['user_id']
                # gid = ev.group_id
                # uid = await select_db(qid, mode='uid')
                # im = await open_push(int(uid[0]), ev.sender['user_id'], str(gid), 'StatusA')
                # await bot.send(ev, im, at_sender=True)
            # except ActionFailed as e:
                # await bot.send(ev, '机器人发送消息失败：{}'.format(e))
                # logger.exception('发送开启推送信息失败')
            # except Exception:
                # await bot.send(ev, '未绑定uid信息！请先在群内绑定你的游戏uid，如：绑定uid119379594', at_sender=True)
                # logger.exception('开启推送失败')
        elif m == '简洁签到报告':
            try:
                if qid in bot.config.SUPERUSERS:
                    _ = await config_check('SignReportSimple', 'OPEN')
                    await bot.send(ev, '成功!', at_sender=True)
                else:
                    return
            except ActionFailed as e:
                await bot.send(ev, '机器人发送消息失败：{}'.format(e))
                logger.exception('发送设置成功信息失败')
            except Exception as e:
                await bot.send(ev, '发生错误 {},请检查后台输出。'.format(e))
                logger.exception('设置简洁签到报告失败')
        elif m == '米游币推送':
            try:
                if qid in bot.config.SUPERUSERS:
                    _ = await config_check('MhyBBSCoinReport', 'OPEN')
                    await bot.send(ev, '米游币推送已开启！\n该选项不会影响到实际米游币获取，仅开启私聊推送！\n*【管理员命令全局生效】', at_sender=True)
                else:
                    return
            except ActionFailed as e:
                await bot.send(ev, '机器人发送消息失败：{}'.format(e))
                logger.exception('发送设置成功信息失败')
            except Exception as e:
                await bot.send(ev, '发生错误 {},请检查后台输出。'.format(e))
                logger.exception('设置米游币推送失败')
    except Exception as e:
        await bot.send(ev, '发生错误 {},请检查后台输出。'.format(e))
        logger.exception('开启功能失败')


# 群聊关闭 自动签到 和 推送树脂提醒 功能
@sv.on_prefix('关闭')
async def close_switch_func(bot: HoshinoBot, ev: CQEvent):
    try:
        at = re.search(r'\[CQ:at,qq=(\d*)]', str(ev.message))
        message = ev.message.extract_plain_text()
        m = ''.join(re.findall('[\u4e00-\u9fa5]', message))

        qid = ev.sender['user_id']

        if m == '自动签到':
            try:
                if at:
                    if qid in bot.config.SUPERUSERS:
                        qid = at.group(1)
                    else:
                        await bot.send(ev, '你没有权限。', at_sender=True)
                        return
                else:
                    qid = ev.sender['user_id']
                uid = await select_db(qid, mode='uid')
                im = await open_push(int(uid[0]), ev.sender['user_id'], 'off', 'StatusB')
                await bot.send(ev, im, at_sender=True)
            except ActionFailed as e:
                await bot.send(ev, '机器人发送消息失败：{}'.format(e))
                logger.exception('发送关闭自动签到信息失败')
            except Exception:
                await bot.send(ev, '未绑定uid信息！请先在群内绑定你的游戏uid，如：绑定uid119379594', at_sender=True)
                logger.exception('关闭自动签到失败')
        # elif m == '推送':
            # try:
                # if at:
                    # if qid in bot.config.SUPERUSERS:
                        # qid = at.group(1)
                    # else:
                        # await bot.send(ev, '你没有权限。', at_sender=True)
                        # return
                # else:
                    # qid = ev.sender['user_id']
                # uid = await select_db(qid, mode='uid')
                # im = await open_push(int(uid[0]), ev.sender['user_id'], 'off', 'StatusA')
                # await bot.send(ev, im, at_sender=True)
            # except ActionFailed as e:
                # await bot.send(ev, '机器人发送消息失败：{}'.format(e))
                # logger.exception('发送关闭推送信息失败')
            # except Exception:
                # await bot.send(ev, '未绑定uid信息！请先在群内绑定你的游戏uid，如：绑定uid119379594', at_sender=True)
                # logger.exception('关闭推送失败')
        elif m == '简洁签到报告':
            try:
                if qid in bot.config.SUPERUSERS:
                    _ = await config_check('SignReportSimple', 'CLOSED')
                    await bot.send(ev, '成功!', at_sender=True)
                else:
                    return
            except ActionFailed as e:
                await bot.send(ev, '机器人发送消息失败：{}'.format(e))
                logger.exception('发送设置成功信息失败')
            except Exception as e:
                await bot.send(ev, '发生错误 {},请检查后台输出。'.format(e))
                logger.exception('设置简洁签到报告失败')
        elif m == '米游币推送':
            try:
                if qid in bot.config.SUPERUSERS:
                    _ = await config_check('MhyBBSCoinReport', 'CLOSED')
                    await bot.send(ev, '米游币推送已关闭！\n该选项不会影响到实际米游币获取，仅关闭私聊推送！\n*【管理员命令全局生效】', at_sender=True)
                else:
                    return
            except ActionFailed as e:
                await bot.send(ev, '机器人发送消息失败：{}'.format(e))
                logger.exception('发送设置成功信息失败')
            except Exception as e:
                await bot.send(ev, '发生错误 {},请检查后台输出。'.format(e))
                logger.exception('设置米游币推送失败')
    except Exception as e:
        await bot.send(ev, '发生错误 {},请检查后台输出。'.format(e))
        logger.exception('关闭功能失败')


# 群聊内 每月统计 功能
@sv.on_fullmatch('每月统计')
async def send_monthly_data(bot: HoshinoBot, ev: CQEvent):
    try:
        uid = await select_db(ev.sender['user_id'], mode='uid')
        uid = uid[0]
        im = await award(uid)
        await bot.send(ev, im, at_sender=True)
    except ActionFailed as e:
        await bot.send(ev, '机器人发送消息失败：{}'.format(e))
        logger.exception('发送每月统计信息失败')
    except Exception:
        await bot.send(ev, '没有找到绑定信息。\n' + CK_HINT, at_sender=True)
        logger.exception('获取每月统计失败')


# 群聊内 签到 功能
@sv.on_fullmatch('签到')
async def get_sing_func(bot: HoshinoBot, ev: CQEvent):
    try:
        uid = await select_db(ev.sender['user_id'], mode='uid')
        uid = uid[0]
        im = await sign(uid)
        await bot.send(ev, im, at_sender=True)
    except ActionFailed as e:
        await bot.send(ev, '机器人发送消息失败：{}'.format(e))
        logger.exception('发送签到信息失败')
    except Exception:
        await bot.send(ev, '没有找到绑定信息。\n' + CK_HINT, at_sender=True)
        logger.exception('签到失败')


# 群聊内 校验Cookies 是否正常的功能，不正常自动删掉
@sv.on_fullmatch('校验全部Cookies')
async def check_cookies(bot: HoshinoBot, ev: CQEvent):
    try:
        raw_mes = await check_db()
        im = raw_mes[0]
        await bot.send(ev, im)
        for i in raw_mes[1]:
            await bot.send_private_msg(user_id=i[0],
                                       message='您绑定的Cookies（uid{}）已失效，以下功能将会受到影响：\n查看完整信息列表\n'
                                               '查看深渊配队\n自动签到/当前状态/每月统计\n'
                                               '请及时重新绑定Cookies并重新开关相应功能。'.format(i[1]))
            await asyncio.sleep(3 + random.randint(1, 3))
    except ActionFailed as e:
        await bot.send(ev, '机器人发送消息失败：{}'.format(e))
        logger.exception('发送Cookie校验信息失败')
    except Exception as e:
        await bot.send(ev, '发生错误 {},请检查后台输出。'.format(e))
        logger.exception('Cookie校验错误')


# 群聊内 校验Stoken 是否正常的功能，不正常自动删掉
@sv.on_fullmatch('校验全部Stoken')
async def check_stoken(bot: HoshinoBot, ev: CQEvent):
    try:
        raw_mes = await check_stoken_db()
        im = raw_mes[0]
        await bot.send(ev, im)
        for i in raw_mes[1]:
            await bot.send_private_msg(user_id=i[0],
                                       message='您绑定的Stoken（uid{}）已失效，以下功能将会受到影响：\n'
                                               '开启自动米游币，开始获取米游币。\n'
                                               '重新添加后需要重新开启自动米游币。'.format(i[1]))
            await asyncio.sleep(3 + random.randint(1, 3))
    except ActionFailed as e:
        await bot.send(ev, '机器人发送消息失败：{}'.format(e))
        logger.exception('发送Cookie校验信息失败')
    except Exception as e:
        await bot.send(ev, '发生错误 {},请检查后台输出。'.format(e))
        logger.exception('Cookie校验错误')


# 群聊内 查询当前树脂状态以及派遣状态 的命令
# @sv.on_fullmatch('当前状态')
# async def send_daily_data(bot: HoshinoBot, ev: CQEvent):
    # try:
        # uid = await select_db(ev.sender['user_id'], mode='uid')
        # uid = uid[0]
        # mes = await daily('ask', uid)
        # im = mes[0]['message']
    # except Exception:
        # im = '没有找到绑定信息。\n' + CK_HINT
        # logger.exception('获取当前状态失败')

    # try:
        # await bot.send(ev, im, at_sender=True)
    # except ActionFailed as e:
        # await bot.send(ev, '机器人发送消息失败：{}'.format(e))
        # logger.exception('发送当前状态信息失败')


# 图片版信息
@sv.on_fullmatch('当前信息')
async def send_genshin_info(bot: HoshinoBot, ev: CQEvent):
    try:
        message = ev.message.extract_plain_text()
        uid = await select_db(ev.sender['user_id'], mode='uid')
        uid = uid[0]
        image = re.search(r'\[CQ:image,file=(.*),url=(.*)]', message)
        im = await draw_info_pic(uid, image)
        try:
            await bot.send(ev, MessageSegment.image(im), at_sender=True)
        except ActionFailed as e:
            await bot.send(ev, '机器人发送消息失败：{}'.format(e))
            logger.exception('发送当前信息信息失败')
    except Exception:
        im = '没有找到绑定信息。\n' + CK_HINT
        await bot.send(ev, im, at_sender=True)
        logger.exception('获取当前信息失败')


# 群聊内 查询uid 的命令
@sv.on_prefix('uid')
async def send_uid_info(bot: HoshinoBot, ev: CQEvent):
    try:
        image = re.search(r'\[CQ:image,file=(.*),url=(.*)]', str(ev.message))
        message = ev.message.extract_plain_text()
        uid = re.findall(r'\d+', message)[0]  # str
        m = ''.join(re.findall('[\u4e00-\u9fa5]', message))
        if m == '深渊':
            try:
                if len(re.findall(r'\d+', message)) == 2:
                    floor_num = re.findall(r'\d+', message)[1]
                    im = await draw_abyss_pic(uid, ev.sender['nickname'], floor_num, image)
                    if im.startswith('base64://'):
                        await bot.send(ev, MessageSegment.image(im), at_sender=True)
                    else:
                        await bot.send(ev, im, at_sender=True)
                else:
                    im = await draw_abyss0_pic(uid, ev.sender['nickname'], image)
                    if im.startswith('base64://'):
                        await bot.send(ev, MessageSegment.image(im), at_sender=True)
                    else:
                        await bot.send(ev, im, at_sender=True)
            except ActionFailed as e:
                await bot.send(ev, '机器人发送消息失败：{}'.format(e))
                logger.exception('发送uid深渊信息失败')
            except TypeError:
                await bot.send(ev, '获取失败，可能是Cookies失效或者未打开米游社角色详情开关。\n或者根本就不存在这个uid.')
                logger.exception('深渊数据获取失败（Cookie失效/不公开信息）')
            except Exception as e:
                await bot.send(ev, '获取失败，有可能是数据状态有问题,\n{}\n请检查后台输出。'.format(e))
                logger.exception('深渊数据获取失败（数据状态问题）')
        elif m == '上期深渊':
            try:
                if len(re.findall(r'\d+', message)) == 2:
                    floor_num = re.findall(r'\d+', message)[1]
                    im = await draw_abyss_pic(uid, ev.sender['nickname'], floor_num, image, 2, '2')
                    if im.startswith('base64://'):
                        await bot.send(ev, MessageSegment.image(im), at_sender=True)
                    else:
                        await bot.send(ev, im, at_sender=True)
                else:
                    im = await draw_abyss0_pic(uid, ev.sender['nickname'], image, 2, '2')
                    if im.startswith('base64://'):
                        await bot.send(ev, MessageSegment.image(im), at_sender=True)
                    else:
                        await bot.send(ev, im, at_sender=True)
            except ActionFailed as e:
                await bot.send(ev, '机器人发送消息失败：{}'.format(e))
                logger.exception('发送uid上期深渊信息失败')
            except TypeError:
                await bot.send(ev, '获取失败，可能是Cookies失效或者未打开米游社角色详情开关。\n或者根本就不存在这个uid.')
                logger.exception('上期深渊数据获取失败（Cookie失效/不公开信息）')
            except Exception as e:
                await bot.send(ev, '获取失败，有可能是数据状态有问题,\n{}\n请检查后台输出。'.format(e))
                logger.exception('上期深渊数据获取失败（数据状态问题）')
        elif m == '':
            try:
                im = await draw_pic(uid, ev.sender['nickname'], image, 2)
                if im.startswith('base64://'):
                    await bot.send(ev, MessageSegment.image(im), at_sender=True)
                else:
                    await bot.send(ev, im, at_sender=True)
            except ActionFailed as e:
                await bot.send(ev, '机器人发送消息失败：{}'.format(e))
                logger.exception('发送uid信息失败')
            except TypeError:
                await bot.send(ev, '获取失败，可能是Cookies失效或者未打开米游社角色详情开关。\n或者根本就不存在这个uid.')
                logger.exception('数据获取失败（Cookie失效/不公开信息）')
            except Exception as e:
                await bot.send(ev, '获取失败，有可能是数据状态有问题,\n{}\n请检查后台输出。'.format(e))
                logger.exception('数据获取失败（数据状态问题）')
        else:
            try:
                if m == '展柜角色':
                    uid_fold = R_PATH / 'enkaToData' / 'player' / str(uid)
                    char_file_list = uid_fold.glob('*')
                    char_list = []
                    for i in char_file_list:
                        file_name = str(i).split('/')[-1]
                        if '\u4e00' <= file_name[0] <= '\u9fff':
                            char_list.append(file_name.split('.')[0])
                    char_list_str = ','.join(char_list)
                    await bot.send(ev, f'UID{uid}当前缓存角色:{char_list_str}', at_sender=True)
                else:
                    char_name = m
                    with open(os.path.join(INDEX_PATH, 'char_alias.json'),
                            'r',
                            encoding='utf8') as fp:
                        char_data = json.load(fp)
                    for i in char_data:
                        if char_name in i:
                            char_name = i
                        else:
                            for k in char_data[i]:
                                if char_name in k:
                                    char_name = i
                    if '旅行者' in char_name:
                        char_name = '旅行者'
                    with open(R_PATH / 'enkaToData' / 'player' / str(uid) / f'{char_name}.json',
                            'r',
                            encoding='utf8') as fp:
                        raw_data = json.load(fp)
                    im = await draw_char_card(raw_data, image)
                    await bot.send(ev, MessageSegment.image(im), at_sender=True)
            except FileNotFoundError:
                await bot.send(ev, f' ', at_sender=False)
                logger.exception('获取信息失败,你可以使用强制刷新命令进行刷新。')
            except ActionFailed as e:
                await bot.send(ev, '机器人发送消息失败：{}'.format(e))
                logger.exception('发送uid信息失败')
            except TypeError:
                await bot.send(ev, '获取失败，可能是Cookies失效或者未打开米游社角色详情开关。')
                logger.exception('数据获取失败（Cookie失效/不公开信息）')
            except Exception as e:
                await bot.send(ev, '获取失败，有可能是数据状态有问题,\n{}\n请检查后台输出。'.format(e))
                logger.exception('数据获取失败（数据状态问题）')
    except Exception as e:
        await bot.send(ev, '发生错误 {},你小子的查询命令里是不是没带上数字？'.format(e))
        logger.exception('uid查询异常')


# 群聊内 绑定uid 的命令，会绑定至当前qq号上
@sv.on_prefix('绑定uid')
async def link_uid_to_qq(bot: HoshinoBot, ev: CQEvent):
    try:
        message = ev.message.extract_plain_text()
        uid = re.findall(r'\d+', message)[0]  # str
        await connect_db(ev.sender['user_id'], uid)
        await bot.send(ev, '绑定uid成功！', at_sender=True)
    except ActionFailed as e:
        await bot.send(ev, '机器人发送消息失败：{}'.format(e))
        logger.exception('发送绑定信息失败')
    except Exception as e:
        await bot.send(ev, '发生错误 {},你小子的查询命令里是不是没带上数字？'.format(e))
        logger.exception('绑定uid异常')


# 群聊内 绑定米游社通行证 的命令，会绑定至当前qq号上，和绑定uid不冲突，两者可以同时绑定
@sv.on_prefix('绑定mys')
async def link_mihoyo_bbs_to_qq(bot: HoshinoBot, ev: CQEvent):
    try:
        message = ev.message.extract_plain_text()
        mys = re.findall(r'\d+', message)[0]  # str
        await connect_db(ev.sender['user_id'], None, mys)
        await bot.send(ev, '绑定米游社id成功！', at_sender=True)
    except ActionFailed as e:
        await bot.send(ev, '机器人发送消息失败：{}'.format(e))
        logger.exception('发送绑定信息失败')
    except Exception as e:
        await bot.send(ev, '发生错误 {},请检查后台输出。'.format(e))
        logger.exception('绑定米游社通行证异常')


# 群聊内 绑定过uid/mysid的情况下，可以查询，默认优先调用米游社通行证，多出世界等级一个参数
@sv.on_prefix('查询')
async def get_info(bot, ev):
    try:
        image = re.search(r'\[CQ:image,file=(.*),url=(.*)]', str(ev.message))
        at = re.search(r'\[CQ:at,qq=(\d*)]', str(ev.raw_message.strip()))
        message = ev.message.extract_plain_text()
        if at:
            qid = at.group(1)
            mi = await bot.get_group_member_info(group_id=ev.group_id, user_id=qid)
            nickname = mi['nickname']
            uid = await select_db(qid)
        else:
            nickname = ev.sender['nickname']
            uid = await select_db(ev.sender['user_id'])

        m = ''.join(re.findall('[\u4e00-\u9fa5]', message))
        if uid:
            if m == '深渊':
                try:
                    if len(re.findall(r'\d+', message)) == 1:
                        floor_num = re.findall(r'\d+', message)[0]
                        im = await draw_abyss_pic(uid[0], nickname, floor_num, image, uid[1])
                        if im.startswith('base64://'):
                            await bot.send(ev, MessageSegment.image(im), at_sender=True)
                        else:
                            await bot.send(ev, im, at_sender=True)
                    else:
                        im = await draw_abyss0_pic(uid[0], nickname, image, uid[1])
                        if im.startswith('base64://'):
                            await bot.send(ev, MessageSegment.image(im), at_sender=True)
                        else:
                            await bot.send(ev, im, at_sender=True)
                except ActionFailed as e:
                    await bot.send(ev, '机器人发送消息失败：{}'.format(e))
                    logger.exception('发送uid深渊信息失败')
                except TypeError:
                    await bot.send(ev, '获取失败，可能是Cookies失效或者未打开米游社角色详情开关。')
                    logger.exception('深渊数据获取失败（Cookie失效/不公开信息）')
                except Exception as e:
                    await bot.send(ev, '获取失败，有可能是数据状态有问题,\n{}\n请检查后台输出。'.format(e))
                    logger.exception('深渊数据获取失败（数据状态问题）')
            elif m == '上期深渊':
                try:
                    if len(re.findall(r'\d+', message)) == 1:
                        floor_num = re.findall(r'\d+', message)[0]
                        im = await draw_abyss_pic(uid[0], nickname, floor_num, image, uid[1], '2')
                        if im.startswith('base64://'):
                            await bot.send(ev, MessageSegment.image(im), at_sender=True)
                        else:
                            await bot.send(ev, im, at_sender=True)
                    else:
                        im = await draw_abyss0_pic(uid[0], nickname, image, uid[1], '2')
                        if im.startswith('base64://'):
                            await bot.send(ev, MessageSegment.image(im), at_sender=True)
                        else:
                            await bot.send(ev, im, at_sender=True)
                except ActionFailed as e:
                    await bot.send(ev, '机器人发送消息失败：{}'.format(e))
                    logger.exception('发送uid上期深渊信息失败')
                except TypeError:
                    await bot.send(ev, '获取失败，可能是Cookies失效或者未打开米游社角色详情开关。')
                    logger.exception('上期深渊数据获取失败（Cookie失效/不公开信息）')
                except Exception as e:
                    await bot.send(ev, '获取失败，有可能是数据状态有问题,\n{}\n请检查后台输出。'.format(e))
                    logger.exception('上期深渊数据获取失败（数据状态问题）')
            elif m == '词云':
                try:
                    im = await draw_word_cloud(uid[0], image, uid[1])
                    if im.startswith('base64://'):
                        await bot.send(ev, MessageSegment.image(im), at_sender=True)
                    else:
                        await bot.send(ev, im, at_sender=True)
                except ActionFailed as e:
                    await bot.send(ev, '机器人发送消息失败：{}'.format(e))
                    logger.exception('发送uid词云信息失败')
                except TypeError:
                    await bot.send(ev, '获取失败，可能是Cookies失效或者未打开米游社角色详情开关。')
                    logger.exception('词云数据获取失败（Cookie失效/不公开信息）')
                except Exception as e:
                    await bot.send(ev, '获取失败，有可能是数据状态有问题,\n{}\n请检查后台输出。'.format(e))
                    logger.exception('词云数据获取失败（数据状态问题）')
            elif m == '收集':
                try:
                    im = await draw_collect_card(uid[0], nickname, image, uid[1])
                    if im.startswith('base64://'):
                        await bot.send(ev, MessageSegment.image(im), at_sender=True)
                    else:
                        await bot.send(ev, im, at_sender=True)
                except ActionFailed as e:
                    await bot.send(ev, '机器人发送消息失败：{}'.format(e))
                    logger.exception('发送uid信息失败')
                except TypeError:
                    await bot.send(ev, '获取失败，可能是Cookies失效或者未打开米游社角色详情开关。')
                    logger.exception('数据获取失败（Cookie失效/不公开信息）')
                except ClientConnectorError:
                    await bot.send(ev, '获取失败：连接超时')
                    logger.exception('连接超时')
                except Exception as e:
                    await bot.send(ev, '获取失败，有可能是数据状态有问题,\n{}\n请检查后台输出。'.format(e))
                    logger.exception('数据获取失败（数据状态问题）')
            elif m == '':
                try:
                    im = await draw_pic(uid[0], nickname, image, uid[1])
                    if im.startswith('base64://'):
                        await bot.send(ev, MessageSegment.image(im), at_sender=True)
                    else:
                        await bot.send(ev, im, at_sender=True)
                except ActionFailed as e:
                    await bot.send(ev, '机器人发送消息失败：{}'.format(e))
                    logger.exception('发送uid信息失败')
                except TypeError:
                    await bot.send(ev, '获取失败，可能是Cookies失效或者未打开米游社角色详情开关。')
                    logger.exception('数据获取失败（Cookie失效/不公开信息）')
                except ClientConnectorError:
                    await bot.send(ev, '获取失败：连接超时')
                    logger.exception('连接超时')
                except Exception as e:
                    await bot.send(ev, '获取失败，有可能是数据状态有问题,\n{}\n或者你根本就没在我这绑定过uid/mys'.format(e))
                    logger.exception('数据获取失败（数据状态问题）')
            else:
                try:
                    if at:
                        qid = at.group(1)
                    else:
                        qid = ev.sender['user_id']
                    uid = await select_db(qid, mode='uid')
                    uid = uid[0]
                    if m == '展柜角色':
                        uid_fold = R_PATH / 'enkaToData' / 'player' / str(uid)
                        char_file_list = uid_fold.glob('*')
                        char_list = []
                        for i in char_file_list:
                            file_name = i.name
                            if '\u4e00' <= file_name[0] <= '\u9fff':
                                char_list.append(file_name.split('.')[0])
                        char_list_str = ','.join(char_list)
                        await bot.send(ev, f'UID{uid}当前缓存角色:{char_list_str}', at_sender=True)
                    else:
                        char_name = m
                        with open(os.path.join(INDEX_PATH, 'char_alias.json'),
                                'r',
                                encoding='utf8') as fp:
                            char_data = json.load(fp)
                        for i in char_data:
                            if char_name in i:
                                char_name = i
                            else:
                                for k in char_data[i]:
                                    if char_name in k:
                                        char_name = i
                        if '旅行者' in char_name:
                            char_name = '旅行者'
                        with open(R_PATH / 'enkaToData' / 'player' / str(uid) / f'{char_name}.json',
                                'r',
                                encoding='utf8') as fp:
                            raw_data = json.load(fp)
                        im = await draw_char_card(raw_data, image)
                        await bot.send(ev, MessageSegment.image(im), at_sender=True)
                except FileNotFoundError:
                    logger.exception('获取信息失败,你可以使用强制刷新命令进行刷新。')
                except Exception:
                    logger.exception('获取信息失败,你可以使用强制刷新命令进行刷新。')
        else:
            await bot.send(ev, '未找到绑定记录！\n' + CK_HINT)
    except Exception as e:
        logger.exception('查询异常')


# 群聊内 查询米游社通行证 的命令
@sv.on_prefix('mys')
async def send_mihoyo_bbs_info(bot: HoshinoBot, ev: CQEvent):
    try:
        image = re.search(r'\[CQ:image,file=(.*),url=(.*)]', str(ev.message))
        message = ev.message.extract_plain_text()
        uid = re.findall(r'\d+', message)[0]  # str
        m = ''.join(re.findall('[\u4e00-\u9fa5]', message))
        if m == '深渊':
            try:
                if len(re.findall(r'\d+', message)) == 2:
                    floor_num = re.findall(r'\d+', message)[1]
                    im = await draw_abyss_pic(uid, ev.sender['nickname'], floor_num, image, 3)
                    if im.startswith('base64://'):
                        await bot.send(ev, MessageSegment.image(im), at_sender=True)
                    else:
                        await bot.send(ev, im, at_sender=True)
                else:
                    im = await draw_abyss0_pic(uid, ev.sender['nickname'], image, 3)
                    if im.startswith('base64://'):
                        await bot.send(ev, MessageSegment.image(im), at_sender=True)
                    else:
                        await bot.send(ev, im, at_sender=True)
            except ActionFailed as e:
                await bot.send(ev, '机器人发送消息失败：{}'.format(e))
                logger.exception('发送米游社深渊信息失败')
            except TypeError:
                await bot.send(ev, '获取失败，可能是Cookies失效或者未打开米游社角色详情开关。')
                logger.exception('深渊数据获取失败（Cookie失效/不公开信息）')
            except Exception as e:
                await bot.send(ev, '数据获取失败，你可能查错了\n这是查询米游社账号的命令而非uid,\n{}\n查询uid请把mys改为uid。'.format(e))
                logger.exception('深渊数据获取失败（数据状态问题）')
        elif m == '上期深渊':
            try:
                if len(re.findall(r'\d+', message)) == 1:
                    floor_num = re.findall(r'\d+', message)[0]
                    im = await draw_abyss_pic(uid, ev.sender['nickname'], floor_num, image, 3, '2')
                    if im.startswith('base64://'):
                        await bot.send(ev, MessageSegment.image(im), at_sender=True)
                    else:
                        await bot.send(ev, im, at_sender=True)
                else:
                    im = await draw_abyss0_pic(uid, ev.sender['nickname'], image, 3, '2')
                    if im.startswith('base64://'):
                        await bot.send(ev, MessageSegment.image(im), at_sender=True)
                    else:
                        await bot.send(ev, im, at_sender=True)
            except ActionFailed as e:
                await bot.send(ev, '机器人发送消息失败：{}'.format(e))
                logger.exception('发送米游社上期深渊信息失败')
            except TypeError:
                await bot.send(ev, '获取失败，可能是Cookies失效或者未打开米游社角色详情开关。')
                logger.exception('上期深渊数据获取失败（Cookie失效/不公开信息）')
            except Exception as e:
                await bot.send(ev, '数据获取失败，你可能查错了\n这是查询米游社账号的命令而非uid,\n{}\n查询uid请把mys改为uid。'.format(e))
                logger.exception('上期深渊数据获取失败（数据状态问题）')
        else:
            try:
                im = await draw_pic(uid, ev.sender['nickname'], image, 3)
                if im.startswith('base64://'):
                    await bot.send(ev, MessageSegment.image(im), at_sender=True)
                else:
                    await bot.send(ev, im, at_sender=True)
            except ActionFailed as e:
                await bot.send(ev, '机器人发送消息失败：{}'.format(e))
                logger.exception('发送米游社信息失败')
            except TypeError:
                await bot.send(ev, '获取失败，可能是Cookies失效或者未打开米游社角色详情开关。')
                logger.exception('米游社数据获取失败（Cookie失效/不公开信息）')
            except Exception as e:
                await bot.send(ev, '数据获取失败，你可能查错了\n这是查询米游社账号的命令而非uid,\n{}\n查询uid请把mys改为uid。'.format(e))
                logger.exception('米游社数据获取失败（数据状态问题）')
    except Exception as e:
        await bot.send(ev, '发生错误 {},\n你小子的查询命令里是不是没带上米游社ID？'.format(e))
        logger.exception('米游社查询异常')
