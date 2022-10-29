import json
import time

import pyqrcode
import requests

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/104.0.0.0 Safari/537.36'}
over_text = '{"code":0,"msg":"","message":"","data":{"has_more":0,"next_offset":0,"_gt_":0}}'
success_text = '{"code":0,"message":"0","ttl":1,"data":{}}'


def timestamp_convert_localdate(timestamp, time_format="%Y/%m/%d %H:%M:%S"):
    timeArray = time.localtime(timestamp)
    styleTime = time.strftime(str(time_format), timeArray)
    return styleTime


def url(uid, offset_id=0):
    return "https://api.vc.bilibili.com/dynamic_svr/v1/" + \
           "dynamic_svr/space_history?host_uid=" + \
           "{}&offset_dynamic_id={}&need_top=1&platform=web".format(uid, offset_id)


def get_bless_info(bless_id):
    return "https://api.vc.bilibili.com/lottery_svr/v1/lottery_svr/lottery_notice?dynamic_id={}".format(bless_id)


def get_del_url(name):
    # return 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/rm_dynamic?csrf={}'.format(name)疑似过时接口
    return 'https://api.bilibili.com/x/dynamic/feed/operate/remove?csrf={}'.format(name)


def get_bless_time(bless_id):
    bres = requests.get(get_bless_info(bless_id), headers=HEADERS)
    jsb = json.loads(bres.text)
    print(jsb)
    try:
        tim = jsb['data']['lottery_time']
    except KeyError:
        print("错误，非标准抽奖")
        tim = -1
    return tim


def load_config():
    with open('config.json') as fc:
        fconfig = json.load(fc)
    return fconfig


def load_delnumbers():
    try:
        with open('var.json') as f:
            svars = json.load(f)
            return svars['del_num']
    except FileNotFoundError:
        print('无上次删除数据，新建文件var.json以保存上次删除数量')
        with open('var.json', 'w') as f:
            svars = {'del_num': 0}
            svars = json.dumps(svars)
            f.write(svars)
        return 0


def save_delnum(d_num):
    with open('var.json', 'w') as f:
        svars = {'del_num': d_num}
        svars = json.dumps(svars)
        f.write(svars)


def login_qrcode():
    while True:
        r = requests.get('http://passport.bilibili.com/qrcode/getLoginUrl', headers=HEADERS)
        req = json.loads(r.text)
        qrcodeurl = req['data']['url']
        oauthKey = req['data']['oauthKey']
        img = pyqrcode.create(qrcodeurl)
        print('已获取二维码，下面将展示二维码，扫描后请关闭二维码。')
        time.sleep(5)
        img.show()
        time.sleep(5)
        logindata = {'oauthKey': oauthKey}
        while True:
            time.sleep(1)
            r = requests.post('http://passport.bilibili.com/qrcode/getLoginInfo', data=logindata, headers=HEADERS)
            loginres = json.loads(r.text)
            if loginres['data'] == -1:
                print('出现错误')
                break
            elif loginres['data'] == -2:
                print('二维码已超时，重新获取二维码')
                time.sleep(1.5)
                break
            elif loginres['data'] == -4:
                print('二维码未扫描，等待扫码')
                time.sleep(0.5)
            elif loginres['data'] == -5:
                print('已扫码，等待确认,如点按取消登录请重新扫码')
                time.sleep(0.5)
            else:
                print('扫码成功')
                time.sleep(1)
                cookies = r.cookies.items()
                uid = cookies[0][1]
                SESSDATA = cookies[2][1]
                csrf = cookies[4][1]
                uuid = ''
                time.sleep(1)
                del req, qrcodeurl, oauthKey, r, logindata, loginres
                return uid, SESSDATA, csrf, uuid

        del req, qrcodeurl, oauthKey, r, logindata, loginres


def post_del_message(dynamicid, cookies):
    del_nynamic_data = {"dyn_id_str": dynamicid}
    re = requests.post(get_del_url(cookies['bili_jct']),
                       data=del_nynamic_data,
                       cookies=cookies,
                       headers=HEADERS)
    print(re.text)
    if re.text == success_text:
        return '删除成功'
    return '删除失败'


if __name__ == '__main__':
    remin = requests.get('https://www.bilibili.com/', headers=HEADERS)
    config = load_config()
    deled_number = load_delnumbers()
    if config['SESSDATA'] == "" or config['bili_jct'] == "" or config['_uuid'] == "" or config['uid'] == 0:
        print('无用户信息或用户信息不完整，程序退出')
        exit()
    #     while True:
    #         loginway = input("请输入登录方式:\n1.二维码扫码登录（推荐）\n2.手机验证码登录（需进行机器人验证）\n"
    #                          "3.账号密码登录（需进行机器人验证）（不推荐）"
    #                          "\n请选择登录方式并输入前的序号:")
    #         if loginway == '1':
    #             qruid, qrSESSDATA, qrcsrf, uuid = login_qrcode()
    #             config['SESSDATA'] = qrSESSDATA
    #             config['uid'] = qruid
    #             config['bili_jct'] = qrcsrf
    #             config['_uuid'] = uuid
    #             del qruid, qrSESSDATA, qrcsrf
    #             cookie = {'SESSDATA': config['SESSDATA'], 'bili_jct': config['bili_jct']}
    #             print('登录成功！\n\n')
    #             break
    #         elif loginway == '2':
    #             print('暂未开发，请选择其他登录方式')
    #             # break
    #         elif loginway == '3':
    #             print('暂未开发，请选择其他登录方式')
    #             # break
    #         else:
    #             print('错误的输入，请输入登录方式前的序号')
    # else:
    #     cookie = {'SESSDATA': config['SESSDATA'], 'bili_jct': config['bili_jct']}
    cookie = {'SESSDATA': config['SESSDATA'], '_uuid': config['_uuid'], 'bili_jct': config['bili_jct']}
    res = requests.get(url(config['uid']), headers=HEADERS)
    while res.text != over_text:
        data = json.loads(res.text)
        print(data)
        data_list = data['data']['cards']
        for data1 in data_list:  # 在获取的列表中循环每个动态
            time.sleep(1)
            card_js = json.loads(data1['card'])
            is_cj = 0
            dy_id = data1['desc']['dynamic_id']
            # print(card_js)
            try:
                print(json.loads(card_js['origin'])['item']['description'])
            except KeyError:
                print('加载文本中keyerror')
            if config['del_all'] == 0:
                print('部分删除模式，即将判断是否抽奖过期')
                try:

                    origin = card_js['origin']
                    origin_js = json.loads(origin)
                    res = origin_js['item']
                    try:
                        res = res['description']
                        ans = res.find('互动抽奖')
                        if ans != -1:
                            is_cj = 1
                    except KeyError:
                        print('这个转发的视频')
                        continue
                except KeyError:
                    print("此动态无原产地信息(非转发或原动态(视频)被删除)")
                if is_cj == 1:
                    ntime = time.time()
                    ntime = int(ntime)
                    dtime = 2592000  # 一周
                    orig_dy_id = card_js['item']['orig_dy_id']
                    print("检查到抽奖动态" + str(dy_id) + ' orig_id:', orig_dy_id)
                    bltime = get_bless_time(orig_dy_id)
                    if bltime == -1:
                        put_timestamp = card_js['item']['timestamp']

                        try:
                            origin = card_js['origin']
                            origin_js = json.loads(origin)
                            res = origin_js['item']
                            print("动态", dy_id, '非标准抽奖。动态文本如下:', origin_js['item']['description'])
                        except KeyError:
                            print("获取转发动态文本失败", dy_id)
                        if put_timestamp + dtime > ntime:
                            print('一月前非标准抽奖，执行删除')
                            print(post_del_message(dy_id, cookie))
                        continue

                    if ntime < bltime:
                        print("本地北京时间:", timestamp_convert_localdate(1632737190))
                        print('未开奖，不删除', dy_id, ' 当前时间', ntime, ' 开奖时间为', bltime)
                    else:
                        print('已开奖，发送删除请求', dy_id, ' 当前时间', ntime, ' 开奖时间为', bltime)
                        print(post_del_message(dy_id, cookie))
                        deled_number = deled_number + 1
                        print('已删除', deled_number, '个')
                        save_delnum(deled_number)
            else:
                print('全部删除模式，即将删除', dy_id)
                time.sleep(1)
                print(post_del_message(dy_id, cookie))
                deled_number = deled_number + 1
                print('已删除', deled_number, '个')
                save_delnum(deled_number)
        nextoffid = data['data']['next_offset']
        res = requests.get(url(config['uid'], nextoffid), headers=HEADERS)
        print('加载下一页 下一页id为', nextoffid)
    print('查询已经结束，删除完成')
