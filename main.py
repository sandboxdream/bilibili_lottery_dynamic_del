import requests
import json
import time


def url(uid, offset_id=0):
    return "https://api.vc.bilibili.com/dynamic_svr/v1/" + \
           "dynamic_svr/space_history?host_uid=" + \
           "{}&offset_dynamic_id={}&need_top=1&platform=web".format(uid, offset_id)


def get_bless_info(bless_id):
    return "https://api.vc.bilibili.com/lottery_svr/v1/lottery_svr/lottery_notice?dynamic_id={}".format(bless_id)


def get_del_url(name):
    return 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/rm_dynamic?csrf={}'.format(name)


def get_bless_time(bless_id):
    bres = requests.get(get_bless_info(bless_id))
    jsb = json.loads(bres.text)
    print(jsb)
    try:
        tim = jsb['data']['lottery_time']
    except KeyError:
        print("错误，非标准抽奖")
        tim = -1
    return tim


over_text = '{"code":0,"msg":"","message":"","data":{"has_more":0,"next_offset":0,"_gt_":0}}'

with open('config.json') as f:
    config = json.load(f)
deled_number = 0
res = requests.get(url(config['uid']))
while res.text != over_text:
    data = json.loads(res.text)
    print(data)
    data_list = data['data']['cards']
    for data1 in data_list:  # 在获取的列表中循环每个动态
        time.sleep(1)
        card_js = json.loads(data1['card'])
        is_cj = 0
        dy_id = data1['desc']['dynamic_id']
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
                print("此动态无原产地信息(非转发)")
            if is_cj == 1:
                ntime = time.time()
                ntime = int(ntime)
                dtime = 2592000  # 一周
                orig_dy_id = card_js['item']['orig_dy_id']
                print("检查到抽奖动态" + str(dy_id) + ' orig_id:', orig_dy_id)
                bltime = get_bless_time(orig_dy_id)
                if bltime == -1:
                    put_timestamp = card_js['item']['timestamp']
                    print(card_js)
                    try:
                        origin = card_js['origin']
                        origin_js = json.loads(origin)
                        res = origin_js['item']
                        print("动态", dy_id, '非标准抽奖。动态文本如下:', origin_js['item']['description'])
                    except KeyError:
                        print("获取转发动态文本失败", dy_id)
                    if put_timestamp + dtime > ntime:
                        print('一月前非标准抽奖，执行删除')
                        cookie = {'_uuid': config['_uuid'],
                                  'SESSDATA': config['SESSDATA']}
                        podata = {'dynamic_id': dy_id}
                        print(requests.post('https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/rm_dynamic',
                                            data=podata,
                                            cookies=cookie).text)
                    continue

                if ntime < bltime:
                    print('未开奖，不删除', dy_id, ' 当前时间', ntime, ' 开奖时间为', bltime)
                else:
                    print('已开奖，发送删除请求', dy_id, ' 当前时间', ntime, ' 开奖时间为', bltime)
                    deled_number = deled_number + 1
                    print('已删除', deled_number, '个')
                    cookie = {'_uuid': config['_uuid'],
                              'SESSDATA': config['SESSDATA']}
                    podata = {'dynamic_id': dy_id}
                    print(requests.post('https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/rm_dynamic',
                                        data=podata,
                                        cookies=cookie).text)
        else:
            print('全部删除模式，即将删除', dy_id)
            time.sleep(1)
            cookie = {'_uuid': config['_uuid'],
                      'SESSDATA': config['SESSDATA']}
            podata = {'dynamic_id': dy_id}

            print(requests.post('https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/rm_dynamic',
                                data=podata,
                                cookies=cookie).text)

    nextoffid = data['data']['next_offset']
    res = requests.get(url(config['uid'], nextoffid))
    print('加载下一页 下一页id为', nextoffid)
print('查询已经结束，删除完成')
