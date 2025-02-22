import math
import os
import sys
from base64 import b64encode
from io import BytesIO
from typing import List

import aiofiles

from openpyxl import load_workbook

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# 忽略PEP8 E402 module level import not at top of file 警告
from .get_data import *  # noqa: E402
from .get_image import draw_event_pic  # noqa: E402
import get_mihoyo_bbs_coin as coin  # noqa: E402

FILE_PATH = os.path.dirname(__file__)
FILE2_PATH = os.path.join(FILE_PATH, 'mihoyo_bbs')
INDEX_PATH = os.path.join(FILE2_PATH, 'index')
Texture_PATH = os.path.join(FILE2_PATH, 'texture2d')

avatar_json = {
    'Jean' :'琴',
    'Lisa' :'丽莎',
    'Barbara' :'芭芭拉',
    'Kaeya' :'凯亚',
    'Diluc' :'迪卢克',
    'Razor' :'雷泽',
    'Amber' :'安柏',
    'Venti' :'温迪',
    'Xiangling' :'香菱',
    'Beidou' :'北斗',
    'Xingqiu' :'行秋',
    'Xiao' :'魈',
    'Ningguang' :'凝光',
    'Klee' :'可莉',
    'Zhongli' :'钟离',
    'Fischl' :'菲谢尔',
    'Bennett' :'班尼特',
    'Tartaglia' :'达达利亚',
    'Noelle' :'诺艾尔',
    'Qiqi' :'七七',
    'Chongyun' :'重云',
    'Ganyu' :'甘雨',
    'Albedo' :'阿贝多',
    'Diona' :'迪奥娜',
    'Mona' :'莫娜',
    'Keqing' :'刻晴',
    'Sucrose' :'砂糖',
    'Xinyan' :'辛焱',
    'Rosaria' :'罗莎莉亚',
    'HuTao' :'胡桃',
    'Kazuha' :'枫原万叶',
    'Yanfei' :'烟绯',
    'Eula' :'优菈',
    'Ayaka' :'神里绫华',
    'Yoimiya' :'宵宫',
    'Shogun' :'雷电将军',
    'Sayu' :'早柚',
    'Kokomi' :'珊瑚宫心海',
    'Sara' :'九条裟罗',
    'Aloy' :'埃洛伊',
    'Thoma' :'托马',
    'Gorou' :'五郎',
    'Itto' :'荒泷一斗',
    'Miko' :'八重神子',
    'heizou' :'鹿野院平藏',
    'Yelan' :'夜兰',
    'Shenhe' :'申鹤',
    'YunJin' :'云堇',
    'Shinobu' :'久岐忍',
    'Ayato' :'神里绫人',
    'Tighnari' :'提纳里',
    'Collei' :'柯莱',
    'Dori' :'多莉',
    'Nilou' :'妮露',
    'Cyno' :'赛诺',
    'Candace' :'坎蒂丝', 
    'Nahida' :'纳西妲',
    'Layla' :'莱依拉',
    'Wanderer' :'流浪者',
    'Faruzan' :'珐露珊',
    'Yaoyao' :'瑶瑶',
    'Alhaitham' :'艾尔海森',
    'Dehya' :'迪希雅',
    'Mika' :'米卡'
}

daily_im = """
*数据刷新可能存在一定延迟，请以当前游戏实际数据为准{}
==============
原粹树脂：{}/{}{}
每日委托：{}/{} 奖励{}领取
减半已用：{}/{}
洞天宝钱：{}
参量质变仪：{}
探索派遣：
总数/完成/上限：{}/{}/{}
{}

如无需该消息提醒请回复 关闭推送 """

month_im = """
==============
{}
UID：{}
==============
本日获取原石：{}
本日获取摩拉：{}
==============
昨日获取原石：{}
昨日获取摩拉：{}
==============
本月获取原石：{}
本月获取摩拉：{}
==============
上月获取原石：{}
上月获取摩拉：{}
==============
原石收入组成：
{}=============="""

weapon_im = """【名称】：{}
【类型】：{}
【稀有度】：{}
【介绍】：{}
【攻击力】：{}{}{}"""

char_info_im = """{}
【稀有度】：{}
【武器】：{}
【元素】：{}
【突破加成】：{}
【生日】：{}
【命之座】：{}
【cv】：{}
【介绍】：{}"""

artifacts_im = """【{}】
【稀有度】：{}
【2件套】：{}
【4件套】：{}
【{}】：{}
【{}】：{}
【{}】：{}
【{}】：{}
【{}】：{}"""

food_im = """【{}】
【稀有度】：{}
【食物类型】：{}
【食物类别】：{}
【效果】：{}
【介绍】：{}
【材料】：
{}"""

audio_json = {
    '357': ['357_01', '357_02', '357_03'],
    '1000000': ['1000000_01', '1000000_02', '1000000_03', '1000000_04', '1000000_05', '1000000_06', '1000000_07'],
    '1000001': ['1000001_01', '1000001_02', '1000001_03'],
    '1000002': ['1000002_01', '1000002_02', '1000002_03'],
    '1000100': ['1000100_01', '1000100_02', '1000100_03', '1000100_04', '1000100_05'],
    '1000101': ['1000101_01', '1000101_02', '1000101_03', '1000101_04', '1000101_05', '1000101_06'],
    '1000200': ['1000200_01', '1000200_02', '1000200_03'],
    '1010201': ['1010201_01'],
    '1000300': ['1000300_01', '1000300_02'],
    '1000400': ['1000400_01', '1000400_02', '1000400_03'],
    '1000500':['1000500_01','1000500_02','1000500_03'],
    '1010000':['1010000_01','1010000_02','1010000_03','1010000_04','1010000_05'],
    '1010001':['1010001_01','1010001_02'],
    '1010100':['1010100_01','1010100_02','1010100_03','1010100_04','1010100_05'],
    '1010200':['1010200_01','1010200_02','1010200_03','1010200_04','1010200_05'],
    '1010300':['1010300_01','1010300_02','1010300_03','1010300_04','1010300_05'],
    '1010301':['1010301_01','1010301_02','1010301_03','1010301_04','1010301_05'],
    '1010400':['1010400_01','1010400_02','1010400_03'],
    '1020000':['1020000_01']
}

char_adv_im = """【{}】
【五星武器】：{}
【四星武器】：{}
【三星武器】：{}
【圣遗物】：
{}"""


async def weapon_adv(name):
    async with aiofiles.open(os.path.join(FILE_PATH, 'char_adv_list.json'), encoding='utf-8') as f:
        adv_li = json.loads(await f.read())
    weapons = {}
    artifacts = {}
    for char, info in adv_li.items():
        char_weapons = []
        char_artifacts = []

        for i in info['weapon'].values():  # 3 stars, 4 stars, 5 stars
            char_weapons.extend(i)
        for i in info['artifact']:
            char_artifacts.extend(i)
        #char_artifacts = list(set(char_artifacts))

        for weapon_name in char_weapons:
            if name in weapon_name:  # fuzzy search
                char_weapon = weapons.get(weapon_name, [])
                char_weapon.append(char)
                weapons[weapon_name] = char_weapon
        for artifact_name in char_artifacts:
            if name in artifact_name:  # fuzzy search
                char_artifact = artifacts.get(artifact_name, [])
                char_artifact.append(char)
                char_artifact = list(set(char_artifact))
                artifacts[artifact_name] = char_artifact

    im = []
    if weapons:
        im.append('✨武器：')
        for k, v in weapons.items():
            im.append(f'{"、".join(v)} 可能会用到【{k}】')
    if artifacts:
        im.append('✨圣遗物：')
        for k, v in artifacts.items():
            im.append(f'{"、".join(v)} 可能会用到【{k}】')
    if im == []:
        im = '没有角色能使用【{}】'.format(name)
    else:
        im = '\n'.join(im)
    return im


async def char_adv(name):
    async with aiofiles.open(os.path.join(FILE_PATH, 'char_adv_list.json'), encoding='utf-8') as f:
        adv_li = json.loads(await f.read())
    for char, info in adv_li.items():
        if name in char:
            im = [f'「{char}」', '-=-=-=-=-=-=-=-=-=-']
            if weapon_5 := info['weapon']['5']:
                im.append(f'推荐5★武器：{"、".join(weapon_5)}')
            if weapon_4 := info['weapon']['4']:
                im.append(f'推荐4★武器：{"、".join(weapon_4)}')
            if weapon_3 := info['weapon']['3']:
                im.append(f'推荐3★武器：{"、".join(weapon_3)}')
            if artifacts := info['artifact']:
                im.append('推荐圣遗物搭配：')
                for arti in artifacts:
                    if len(arti) > 1:
                        im.append(f'[{arti[0]}]两件套 + [{arti[1]}]两件套')
                    else:
                        im.append(f'[{arti[0]}]四件套')
            if remark := info['remark']:
                im.append('-=-=-=-=-=-=-=-=-=-')
                im.append('备注：')
                mark = "\n".join(remark)
                im.append(f'{mark}')
            return '\n'.join(im)

    return '没有找到角色信息'


async def deal_ck(mes, qid):
    if 'stoken' in mes:
        login_ticket = re.search(r'login_ticket=([0-9a-zA-Z]+)', mes).group(0).split('=')[1]
        uid = await select_db(qid, 'uid')
        # mys_id = re.search(r'login_uid=([0-9]+)', mes).group(0).split('=')[1]
        ck = await owner_cookies(uid[0])
        mys_id = re.search(r'account_id=(\d*)', ck).group(0).split('=')[1]
        raw_data = await get_stoken_by_login_ticket(login_ticket, mys_id)
        stoken = raw_data['data']['list'][0]['token']
        s_cookies = 'stuid={};stoken={}'.format(mys_id, stoken)
        await stoken_db(s_cookies, uid[0])
        return '添加Stoken成功！'
    else:
        if 'v2' in mes:
            aid = re.search(r'login_uid=(\d*)', mes)
            mysid_data = aid.group(0).split('=')
            mysid = mysid_data[1]
            cookie = ';'.join(filter(lambda x: x.split('=')[0] in [
            'cookie_token_v2', 'login_uid', 'ltmid_v2','ltoken_v2'], [i.strip() for i in mes.split(';')]))
            cookie = cookie+";_gat=1;"
            mys_data = await get_mihoyo_bbs_info(mysid, cookie)
        else:
            aid = re.search(r'account_id=(\d*)', mes)
            mysid_data = aid.group(0).split('=')
            mysid = mysid_data[1]
            cookie = ';'.join(filter(lambda x: x.split('=')[0] in [
                'cookie_token', 'account_id'], [i.strip() for i in mes.split(';')]))
            mys_data = await get_mihoyo_bbs_info(mysid, cookie)
        for i in mys_data['data']['list']:
            if i['game_id'] != 2:
                mys_data['data']['list'].remove(i)
        uid = mys_data['data']['list'][0]['game_role_id']

        conn = sqlite3.connect('ID_DATA.db')
        c = conn.cursor()

        try:
            c.execute('DELETE from CookiesCache where uid=? or mysid = ?', (uid, mysid))
        except:
            pass

        conn.commit()
        conn.close()

        await cookies_db(uid, cookie, qid)
        info = ''
        try:
            login_ticket = re.search(r'login_ticket=([0-9a-zA-Z]+)', mes).group(0).split('=')[1]
            uida = await select_db(qid, 'uid')
            # cookie_token = re.search(r'cookie_token=(\d*)', mes).group(0).split('=')[1]
            mys_id = re.search(r'account_id=(\d*)', mes).group(0).split('=')[1]
            raw_data = await get_stoken_by_login_ticket(login_ticket, mys_id)
            stoken = raw_data['data']['list'][0]['token']
            s_cookies = 'stuid={};stoken={}'.format(mys_id, stoken)
            await stoken_db(s_cookies, uida[0])
            info = 'stoken绑定成功！绑定一次就可以了，请不要重复绑定stoken。'
        except:
            info = 'stoken未绑定！'
        return f'绑定Cookie成功！{info}\n请勿点击退出账号，否则Cookie将失效。'


async def award(uid):
    data = await get_award(uid)
    nickname = data['data']['nickname']
    day_stone = data['data']['day_data']['current_primogems']
    day_mora = data['data']['day_data']['current_mora']
    lastday_stone = data['data']['day_data']['last_primogems']
    lastday_mora = data['data']['day_data']['last_mora']
    month_stone = data['data']['month_data']['current_primogems']
    month_mora = data['data']['month_data']['current_mora']
    lastmonth_stone = data['data']['month_data']['last_primogems']
    lastmonth_mora = data['data']['month_data']['last_mora']
    group_str = ''
    for i in data['data']['month_data']['group_by']:
        group_str = group_str + \
                    i['action'] + '：' + str(i['num']) + \
                    '（' + str(i['percent']) + '%）' + '\n'

    im = month_im.format(nickname, uid, day_stone, day_mora, lastday_stone, lastday_mora,
                         month_stone, month_mora, lastmonth_stone, lastmonth_mora, group_str)
    return im


async def audio_wiki(name, message):
    async def get(_audioid):
        for _ in range(3):  # 重试3次
            if _audioid in audio_json:
                if not audio_json[_audioid]:
                    return
                audioid1 = random.choice(audio_json[_audioid])
            else:
                audioid1 = _audioid
            url = await get_audio_info(name, audioid1)
            async with AsyncClient() as client:
                req = await client.get(url)
            if req.status_code == 200:
                return BytesIO(req.content)
            else:
                if _audioid in audio_json:
                    audio_json[_audioid].remove(audioid1)

    if name == '列表':
        with open(os.path.join(INDEX_PATH, '语音.png'), 'rb') as f:
            imgmes = f.read()
        return imgmes
    elif name == '':
        return '请输入角色名。'
    else:
        audioid = re.findall(r'\d+', message)
        try:
            audio = await get(audioid[0])
        except IndexError:
            return '请输入语音ID。'
        except:
            return '语音获取失败'
        if audio:
            return audio.getvalue()
        else:
            return '没有找到语音，请检查语音ID与角色名是否正确，如无误则可能未收录该语音'


async def artifacts_wiki(name):
    data = await get_misc_info('artifacts', name)
    if 'errcode' in data:
        im = '该圣遗物不存在。'
    else:
        star = ''
        for i in data['rarity']:
            star = star + i + '星、'
        star = star[:-1]
        im = artifacts_im.format(data['name'], star, data['2pc'], data['4pc'], data['flower']['name'],
                                 data['flower']['description'],
                                 data['plume']['name'], data['plume']['description'], data['sands']['name'],
                                 data['sands']['description'],
                                 data['goblet']['name'], data['goblet']['description'], data['circlet']['name'],
                                 data['circlet']['description'])
    return im


async def foods_wiki(name):
    data = await get_misc_info('foods', name)
    if 'errcode' in data:
        im = '该食物不存在。'
    else:
        ingredients = ''
        food_temp = {}
        for i in data['ingredients']:
            if i['name'] not in food_temp:
                food_temp[i['name']] = i['count']
            else:
                food_temp[i['name']] = food_temp[i['name']] + i['count']
        for i in food_temp:
            ingredients += i + ':' + str(food_temp[i]) + '\n'
        ingredients = ingredients[:-1]
        im = food_im.format(data['name'], data['rarity'], data['foodtype'], data['foodfilter'], data['effect'],
                            data['description'], ingredients)
    return im


async def enemies_wiki(name):
    raw_data = await get_misc_info('enemies', name)
    if 'errcode' in raw_data:
        im = '该原魔不存在。'
    else:
        reward = ''
        for i in raw_data['rewardpreview']:
            reward += i['name'] + '：' + str(i['count']) if 'count' in i.keys() else i['name'] + '：' + '可能'
            reward += '\n'
        im = '【{}】\n——{}——\n类型：{}\n信息：{}\n掉落物：\n{}'.format(raw_data['name'], raw_data['specialname'],
                                                           raw_data['category'], raw_data['description'], reward)
    return im


# 签到函数
async def sign(uid):
    try:
        sign_data = await mihoyo_bbs_sign(uid)
        sign_info = await get_sign_info(uid)
        sign_info = sign_info['data']
        sign_list = await get_sign_list()
        status = sign_data['message']
        getitem = sign_list['data']['awards'][int(
            sign_info['total_sign_day']) - 1]['name']
        getnum = sign_list['data']['awards'][int(
            sign_info['total_sign_day']) - 1]['cnt']
        get_im = f'本次签到获得{getitem}x{getnum}'
        if status == 'OK' and sign_info['is_sign'] == True:
            mes_im = '签到成功'
        else:
            mes_im = status
        sign_missed = sign_info['sign_cnt_missed']
        im = mes_im + '!' + '\n' + get_im + '\n' + f'本月漏签次数：{sign_missed}'
    except:
        im = '签到失败\n或许是你没有在诺艾尔这里绑定过cookie\n也有可能是你的cookie已失效\n请重新绑定cookie，绑定方法请回复 绑定 查看。'
    return im


# 统计状态函数
async def daily(mode='push', uid=None):
    def seconds2hours(seconds: int) -> str:
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        return '%02d:%02d:%02d' % (h, m, s)

    temp_list = []
    conn = sqlite3.connect('ID_DATA.db')
    c = conn.cursor()
    c_data = None
    if mode == 'push':
        cursor = c.execute(
            'SELECT *  FROM NewCookiesTable WHERE StatusA != ?', ('off',))
        c_data = cursor.fetchall()
    elif mode == 'ask':
        c_data = ([uid, 0, 0, 0, 0, 0, 0],)

    for row in c_data:
        raw_data = await get_daily_data(str(row[0]))
        if raw_data['retcode'] != 0:
            temp_list.append(
                {'qid': row[2], 'gid': row[3], 'message': '你的推送状态有误；可能是uid绑定错误或没有在米游社打开“实时便筏”功能\n也有可能是米游社个人中心里出了验证码。'})
        else:
            dailydata = raw_data['data']
            current_resin = dailydata['current_resin']

            current_expedition_num = dailydata['current_expedition_num']
            max_expedition_num = dailydata['max_expedition_num']
            finished_expedition_num = 0
            expedition_info: List[str] = []
            for expedition in dailydata['expeditions']:
                avatar: str = expedition['avatar_side_icon'][89:-4]
                try:
                    avatar_name: str = avatar_json[avatar]
                except KeyError:
                    avatar_name: str = avatar

                if expedition['status'] == 'Finished':
                    expedition_info.append(f'{avatar_name} 探索完成')
                    finished_expedition_num += 1
                else:
                    remained_timed: str = seconds2hours(
                        expedition['remained_time'])
                    expedition_info.append(
                        f'{avatar_name} 剩余时间{remained_timed}')

            if dailydata['transformer']['recovery_time']['reached']:
                transformer_status = '可用'
            else:
                transformer_time = dailydata['transformer']['recovery_time']
                transformer_status = '还剩{}天{}小时{}分钟可用'.format(transformer_time['Day'], transformer_time['Hour'],
                                                              transformer_time['Minute'])

            # 推送条件检查，在指令查询时 row[6] 为 0 ，而自动推送时 row[6] 为 140，这样保证用指令查询时必回复
            # 说实话我仔细看了一会才理解…
            if current_resin >= row[6] or dailydata['max_home_coin'] - dailydata['current_home_coin'] <= 100:
                tip = ''
                tips = []
                if current_resin >= row[6] != 0:
                    tips.append('我的天，快看你的树脂！')
                if dailydata['max_home_coin'] - dailydata['current_home_coin'] <= 100:
                    tips.append('我的天，快看你的洞天宝钱！')
                if finished_expedition_num == current_expedition_num:
                    tips.append('我的天，快看你的探索派遣！')  # emmmm
                if tips:
                    tips.insert(0, '\n==============')
                    tip = '\n'.join(tips)

                max_resin = dailydata['max_resin']
                rec_time = ''
                # logger.info(dailydata)
                if current_resin < 160:
                    resin_recovery_time = seconds2hours(
                        dailydata['resin_recovery_time'])
                    next_resin_rec_time = seconds2hours(
                        8 * 60 - ((dailydata['max_resin'] - dailydata['current_resin']) * 8 * 60 - int(
                            dailydata['resin_recovery_time'])))
                    rec_time = f' ({next_resin_rec_time}/{resin_recovery_time})'

                finished_task_num = dailydata['finished_task_num']
                total_task_num = dailydata['total_task_num']
                is_extra_got = '已' if dailydata['is_extra_task_reward_received'] else '未'

                resin_discount_num_limit = dailydata['resin_discount_num_limit']
                used_resin_discount_num = resin_discount_num_limit - \
                                          dailydata['remain_resin_discount_num']

                home_coin = f'{dailydata["current_home_coin"]}/{dailydata["max_home_coin"]}'
                if dailydata['current_home_coin'] < dailydata['max_home_coin']:
                    coin_rec_time = seconds2hours(int(dailydata['home_coin_recovery_time']))
                    coin_add_speed = math.ceil((dailydata['max_home_coin'] - dailydata['current_home_coin']) / (
                            int(dailydata['home_coin_recovery_time']) / 60 / 60))
                    home_coin += f'（{coin_rec_time} 约{coin_add_speed}/h）'

                expedition_data = '\n'.join(expedition_info)
                send_mes = daily_im.format(tip, current_resin, max_resin, rec_time, finished_task_num, total_task_num,
                                           is_extra_got, used_resin_discount_num,
                                           resin_discount_num_limit, home_coin, transformer_status,
                                           current_expedition_num, finished_expedition_num,
                                           max_expedition_num, expedition_data)

                temp_list.append(
                    {'qid': row[2], 'gid': row[3], 'message': send_mes})
    return temp_list


async def mihoyo_coin(qid, s_cookies=None):
    uid = await select_db(qid, mode='uid')
    uid = uid[0]
    if s_cookies is None:
        s_cookies = await get_stoken(uid)

    if s_cookies:
        get_coin = coin.MihoyoBBSCoin(s_cookies)
        im = await get_coin.task_run()
    else:
        im = '秋豆麻袋~，你还没有绑定Stoken，无法使用这个功能呢\n回复 绑定Stoken 查看绑定方法'
    return im


async def get_event_pic():
    img_path = os.path.join(FILE2_PATH, 'event.jpg')
    while True:
        if os.path.exists(img_path):
            f = open(img_path, 'rb')
            ls_f = b64encode(f.read()).decode()
            img_mes = 'base64://' + ls_f
            f.close()
            break
        else:
            await draw_event_pic()
    return img_mes


async def weapon_wiki(name, level=None):
    data = await get_weapon_info(name)
    if 'errcode' in data:
        im = '该武器不存在。'
    elif level:
        data2 = await get_weapon_info(name, level)
        if data['substat'] != '':
            sp = data['substat'] + '：' + '%.1f%%' % (data2['specialized'] * 100) \
                if data['substat'] != '元素精通' else data['substat'] + '：' + str(math.floor(data2['specialized']))
        else:
            sp = ''
        im = (data['name'] + '\n等级：' + str(data2['level']) + '（突破' + str(data2['ascension']) + '）' +
              '\n攻击力：' + str(round(data2['attack'])) + '\n' + sp)
    else:
        name = data['name']
        _type = data['weapontype']
        star = data['rarity'] + '星'
        info = data['description']
        atk = str(data['baseatk'])
        sub_name = data['substat']
        if data['subvalue'] != '':
            sub_val = (data['subvalue'] +
                       '%') if sub_name != '元素精通' else data['subvalue']
            sub = '\n' + '【' + sub_name + '】' + sub_val
        else:
            sub = ''

        if data['effectname'] != '':
            raw_effect = data['effect']
            rw_ef = []
            for i in range(len(data['r1'])):
                now = ''
                for j in range(1, 6):
                    now = now + data['r{}'.format(j)][i] + '/'
                now = now[:-1]
                rw_ef.append(now)
            raw_effect = raw_effect.format(*rw_ef)
            effect = '\n' + '【' + data['effectname'] + '】' + '：' + raw_effect
        else:
            effect = ''
        im = weapon_im.format(name, _type, star, info, atk,
                              sub, effect)
    return im


async def char_wiki(name, mode='char', level=None):
    im = ''
    data = await get_char_info(name, mode, level if mode == 'char' else None)
    if mode == 'char':
        if isinstance(data, list):
            im = ','.join(data)
        elif 'errcode' in data:
            im = '不存在该角色或类型。'
        elif level:
            data2 = await get_char_info(name, mode)
            sp = data2['substat'] + '：' + '%.1f%%' % (data['specialized'] * 100) if data2['substat'] != '元素精通' else \
                data2['substat'] + '：' + str(math.floor(data['specialized']))
            im = (data2['name'] + '\n等级：' + str(data['level']) + '\n血量：' + str(math.floor(data['hp'])) +
                  '\n攻击力：' + str(math.floor(data['attack'])) + '\n防御力：' + str(math.floor(data['defense'])) +
                  '\n' + sp)
        else:
            name = data['title'] + ' — ' + data['name']
            star = data['rarity']
            _type = data['weapontype']
            element = data['element']
            up_val = data['substat']
            bdday = data['birthday']
            polar = data['constellation']
            cv = data['cv']['chinese']
            info = data['description']
            im = char_info_im.format(
                name, star, _type, element, up_val, bdday, polar, cv, info)
    elif mode == 'costs':
        if isinstance(data[1], list):
            im = ','.join(data[1])
        elif 'errcode' in data[1]:
            im = '不存在该角色或类型。'
        else:
            im = '【天赋材料(一份)】\n{}\n【突破材料】\n{}'
            im1 = ''
            im2 = ''

            talent_temp = {}
            talent_cost = data[1]
            for i in talent_cost.values():
                for j in i:
                    if j['name'] not in talent_temp:
                        talent_temp[j['name']] = j['count']
                    else:
                        talent_temp[j['name']] = talent_temp[j['name']] + j['count']
            for k in talent_temp:
                im1 = im1 + k + ':' + str(talent_temp[k]) + '\n'

            temp = {}
            cost = data[0]
            for i in range(1, 7):
                for j in cost['ascend{}'.format(i)]:
                    if j['name'] not in temp:
                        temp[j['name']] = j['count']
                    else:
                        temp[j['name']] = temp[j['name']] + j['count']

            for k in temp:
                im2 = im2 + k + ':' + str(temp[k]) + '\n'

            im = im.format(im1, im2)
    elif mode == 'constellations':
        if 'errcode' in data:
            im = '不存在该角色或命座数量。'
        else:
            im = '【' + data['c{}'.format(level)]['name'] + '】' + '：' + \
                 '\n' + data['c{}'.format(level)]['effect'].replace('*', '')
    elif mode == 'talents':
        if 'errcode' in data:
            im = '不存在该角色。'
        else:
            if 7 >= int(level) > 0:
                if int(level) <= 3:
                    if level == '1':
                        data = data['combat1']
                    elif level == '2':
                        data = data['combat2']
                    elif level == '3':
                        data = data['combat3']
                    skill_name = data['name']
                    skill_info = data['info']
                    skill_detail = ''

                    """
                    for i in data['attributes']['parameters']:
                        temp = ''
                        for k in data['attributes']['parameters'][i]:
                            if str(k).count('.') == 1:
                                temp += '%.2f%%' % (k * 100) + '/'
                            else:
                                temp = k
                                break
                        data['attributes']['parameters'][i] = temp[:-1]

                    for i in data['attributes']['labels']:
                        #i = i.replace('{','{{')
                        i = re.sub(r':[a-zA-Z0-9]+}', '}', i)
                        #i.replace(r':[a-zA-Z0-9]+}','}')
                        skill_detail += i + '\n'

                    skill_detail = skill_detail.format(**data['attributes']['parameters'])
                    """
                    mes_list = []
                    parameters = []
                    add_switch = True

                    labels = ''.join(data['attributes']['labels'])
                    parameters_label = re.findall(r'{[a-zA-Z0-9]+:[a-zA-Z0-9]+}', labels)

                    labels = {}
                    for i in parameters_label:
                        value_type = i.replace('{', '').replace('}', '').split(':')[-1]
                        value_index = i.replace('{', '').replace('}', '').split(':')[0]
                        labels[value_index] = value_type
                    
                    for para in data['attributes']['parameters']:
                        if para in labels:
                            label_str = labels[para]
                            for index, j in enumerate(data['attributes']['parameters'][para]):
                                if add_switch:
                                    parameters.append({})

                                if label_str == 'F1P':
                                    parameters[index].update({para: '%.1f%%' % (j * 100)})
                                if label_str == 'F2P':
                                    parameters[index].update({para: '%.2f%%' % (j * 100)})
                                elif label_str == 'F1':
                                    parameters[index].update({para: '%.1f' % j})
                                elif label_str == 'F2':
                                    parameters[index].update({para: '%.2f' % j})
                                elif label_str == 'P':
                                    parameters[index].update({para: str(round(j * 100)) + '%'})
                                elif label_str == 'I':
                                    parameters[index].update({para: '%.2f' % j})
                            add_switch = False

                    for k in data['attributes']['labels']:
                        k = re.sub(r':[a-zA-Z0-9]+}', '}', k)
                        skill_detail += k + '\n'

                    skill_detail = skill_detail[:-1].replace('|', ' | ')

                    for i in range(1, 10):
                        if i % 2 != 0:
                            skill_info = skill_info.replace('**', '「', 1)
                        else:
                            skill_info = skill_info.replace('**', '」', 1)

                    mes_list.append({
                        'type': 'node',
                        'data': {
                            'name'   : '西风骑士团实习生-诺艾尔',
                            'uin'    : '575075708',
                            'content': '【' + skill_name + '】' + '\n' + skill_info
                        }
                    })

                    for index, i in enumerate(parameters):
                        mes = skill_detail.format(**i)
                        node_data = {
                            'type': 'node',
                            'data': {
                                'name'   : '西风骑士团实习生-诺艾尔',
                                'uin'    : '575075708',
                                'content': 'lv.' + str(index + 1) + '\n' + mes
                            }
                        }
                        mes_list.append(node_data)
                    im = mes_list

                else:
                    if level == '4':
                        data = data['passive1']
                    elif level == '5':
                        data = data['passive2']
                    elif level == '6':
                        data = data['passive3']
                    elif level == '7':
                        data = data['passive4']
                    skill_name = data['name']
                    skill_info = data['info']
                    im = '【{}】\n{}'.format(skill_name, skill_info)
            else:
                im = '不存在该天赋。'
    return im
