import mysql.connector
import numpy as np
from tool.tool import *
import unicodedata

host = '127.0.0.1'
user = 'root'
password = 'chujiao'
database = 'sys'

if "PYCHARM_HOSTED" in os.environ:
    schema = 'douyin'
else:
    schema = 'douyin'

user_info_table_name = 'user_info'
user_info_liuzi_table_name = 'user_info_留资'
device_table_name = 'common.device'
log_table_name = 'common.api_log'

guanzhu_table_name = '关注'
greet_table_name = '打招呼'
reply_table_name = '回复'
liuzi_table_name = '留资'
dianzan_table_name = '点赞'
chat_table_name = '聊天记录'

homepage_start = 'https://www.douyin.com/user/'

like_types = [None, '', '未关注', '正在关注', '已关注', '关注失败']
greet_types = [None, '', '未打招呼', '正在打招呼', '已打招呼', '打招呼失败']
reply_types = [None, '', '未回复', '已回复']
#big_cities = ['北京','上海','重庆','天津']
big_cities = []
#zhixiashi = ['北京','上海','重庆','天津']

def connect_to_db():
    while True:
        try:
            conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            cursor = conn.cursor()
            break
        except Exception as e:
            try:
                cursor.close()
            except:
                pass
            try:
                conn.close()
            except:
                pass
            print(e)
    return conn, cursor


def conn_cursor_exception(conn, cursor, e):
    try:
        cursor.close()
    except:
        pass
    try:
        conn.close()
    except:
        pass
    raise ValueError(e)


def double_single_quotes(s):
    s = s.replace('\'', '\'\'')
    s = s.replace('\\', '\\\\')
    return s


def get_insert_sql_str(sets):
    sets2 = sets.copy()
    for k in sets2:
        if type(sets2[k]) in [dict, str]:
            sets2[k] = double_single_quotes(str(sets2[k]))
    keys = ', '.join(sets2.keys())
    values = ', '.join(f"'{v}'" for v in sets2.values())
    sql = f"({keys}) VALUES ({values})"
    return sql


def write_log_to_db(ps, biz):
    conn, cursor = connect_to_db()
    if type(ps)==list:
        p2 = {}
        for p in ps:
            p2.update(p)
    else:
        p2 = ps

    p2['log_time'] = datetime_str()
    if biz:
        p2['biz'] = biz
    try:
        insert_str = get_insert_sql_str(p2)
        sql = f"INSERT IGNORE INTO {log_table_name} {insert_str}"
        cursor.execute(sql)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        try:
            cursor.close()
        except:
            pass
        try:
            conn.close()
        except:
            pass
        print(f"{datetime_str()}, write log error: {str(e)}")


def print_sql(sql, biz=None):
    print(f"sql: {sql}")
    write_log_to_db({'sql_str':sql}, biz)


def get_biz_from(filters):
    change_key(filters, 'agent', '抖音号')
    filter_str = get_filter_str(filters)
    sql = f"SELECT biz FROM {device_table_name} WHERE {filter_str}"
    res = query_sql(sql)
    if len(res)==0:
        err = f"没找到符合条件的设备：" + filter_str
        raise ValueError(err)
    return res[0]['biz']


def get_new_homepage_sql(filters, city, sets, num, schema2):
    sql = f"SELECT 主页,{schema2}.{user_info_table_name}.uid,城市,{schema2}.{user_info_table_name}.昵称,性别,丢弃过滤,复检 FROM {schema2}.{user_info_table_name} LEFT JOIN {schema2}.{greet_table_name} ON {schema2}.{user_info_table_name}.uid=打招呼.uid WHERE "
    filter_str = get_filter_str(filters)
    sql += filter_str
    if city is None:
        sql2 = f"SELECT 任务地点 FROM {device_table_name} WHERE 抖音号='{sets['agent']}'"
        res = query_sql(sql2, schema2)
        if len(res) == 0:
            raise ValueError(f"找不到设备")
        city = res[0]['任务地点']
    if city is not None:
        if city in big_cities:
            sql += f" AND (城市 like '%{city}-{city}%' or 城市='{city}-')"
        else:
            sql += f" AND 城市 like '%{city}%'"
    sql += f" ORDER BY 更新时间 DESC LIMIT {num}"
    return sql


def get_new_homepages_for_city(city,type, schema2, days=-1):
    if type=='存':
        sql = f"SELECT count(*) FROM {schema2}.{user_info_table_name} LEFT JOIN {schema2}.{greet_table_name} ON {schema2}.{user_info_table_name}.uid=打招呼.uid WHERE {schema2}.{greet_table_name}.uid is NULL and 丢弃='' and 复检!='0'"
#        sql = f"SELECT count(*) FROM {schema2}.{user_info_table_name} LEFT JOIN {schema2}.{greet_table_name} ON {schema2}.{user_info_table_name}.uid=打招呼.uid WHERE {schema2}.{greet_table_name}.uid is NULL and 性别='男' and 丢弃='' and 复检!='0'"
    if type=='产':
        sql = f"SELECT count(*) FROM {schema2}.{user_info_table_name} WHERE 性别='男' and 丢弃='' and 复检!='0'"
    if days>0:
        date_s = date_str(-days + 1)
        sql += f" AND 更新时间>'{date_s}'"
    if city in big_cities:
        sql += f" AND (城市 like '%{city}-{city}%' or 城市='{city}-')"
    else:
        sql += f" AND 城市 like '%{city}%'"
    ret = query_sql(sql, schema2,logging=False)
    return ret[0]['count(*)']


def get_newest_unowned_homepage_and_set_status(param, schema2):
    param = param.copy()
    suc = False
    city = split_item_from_param(param,'城市')
    num = split_num_from_arg(param)
    filters = split_items_from_param(param,['性别'])
    filters['打招呼.uid']=None
    filters['质检']='通过'
    filters['丢弃']=''
    filters['复检']='1'
    filters['丢弃过滤']='完成'
    sets = split_items_from_param(param, ['agent'])
    if filters.get('性别') not in [None, '男', '女', '全部']:
        raise ValueError(f"sex 不支持参数[{filters.get('性别')}]")
    if filters.get('性别') == '全部':
        del filters['性别']
    if len(param)>0:
        raise ValueError(f"不支持参数{list(param.keys())}")
    sql = get_new_homepage_sql(filters, city, sets, num, schema2)
    res = query_sql(sql, schema2)
    if res==[]:
        filters['丢弃过滤']=''
        sql = get_new_homepage_sql(filters, city, sets, num, schema2)
        res = query_sql(sql, schema2)
        if res==[]:
            filters['复检'] = ''
            filters['丢弃过滤']='完成'
            sql = get_new_homepage_sql(filters, city, sets, num, schema2)
            res = query_sql(sql, schema2)
            if res==[]:
                filters['丢弃过滤']=''
                sql = get_new_homepage_sql(filters, city, sets, num, schema2)
                res = query_sql(sql, schema2)

    if len(res)>0:
        for result_dict in res:
            sets['uid']=result_dict['uid']
            sets['昵称']=result_dict['昵称']
            sets['打招呼状态']='未打招呼'
            sets['分配时间']=datetime_str()
            insert_str = get_insert_sql_str(sets)
            sql = f"INSERT INTO {schema2}.{greet_table_name} {insert_str}"

            execute_sql(sql, schema2)
            if '城市' in result_dict:
                result_dict['city'] = result_dict['城市']
                del result_dict['城市']
            if '昵称' in result_dict:
                result_dict['nickname'] = result_dict['昵称']
                del result_dict['昵称']
            if '主页' in result_dict:
                result_dict['homepage'] = result_dict['主页']
                del result_dict['主页']
    suc = True

    return suc, res


def release_homepage_by_agent(param, schema2):
    param = param.copy()
    homepage = param.get('主页',None)
    uid = param.get('uid',None)
    filters = split_items_from_param(param, ['agent','主页','uid'])
    if len(param) > 0:
        raise ValueError(f"不支持参数{list(param.keys())}")
    if homepage is None and uid is None:
        err = 'homepage 和 uid 至少要提供一个'
        raise ValueError(err)
    try:
        sql = f"delete from {schema2}.{greet_table_name} WHERE "
        filter_str = get_filter_str(filters)
        sql += filter_str
        updated_rows = execute_sql(sql, schema2)
    except Exception as e:
        print(e)
    if updated_rows == 0:
        err = '没找到符合条件的用户：'+filter_str
        raise ValueError(err)
    return True


def split_items_from_param(param, names):
    items = {}
    for k in list(param.keys()):
        if k in names:
            items[k]=param[k]
            del param[k]
    return items


def split_item_from_param(param, name):
    item = None
    if name in param:
        item = param[name]
        del param[name]
    return item


def change_key(d, from_key, to_key):
    if from_key in d:
        d[to_key] = d[from_key]
        del d[from_key]


def get_set_str(sets):
    set_str = ''
    for k in sets:
        set_str += f", {k}='{sets[k]}'"
    if set_str.startswith(', '):
        set_str = set_str[2:]
    return set_str


def get_filter_str(filters):
    filter_str = ''
    for k in filters:
        if filters[k] is None:
            filter_str += f" AND {k} IS NULL"
        else:
            filter_str += f" AND {k}='{filters[k]}'"
    if filter_str.startswith(' AND '):
        filter_str = filter_str[5:]
    return filter_str


def is_invisible(character):
    category = unicodedata.category(character)
    return category in ['Cf', 'Cn', 'Co', 'Cs', 'Mn']


def update_with_user_nickname(table_name, agent, user_nickname, uid, sets, schema2, allow_not_found=True):
    uid, user_nickname = check_uid_with_user_nickname(agent, user_nickname, uid, schema2, allow_not_found=True)
    if table_name==liuzi_table_name and uid is None:
        uid, user_nickname = check_uid_with_user_nickname(agent, user_nickname, uid, schema2, table_name=dianzan_table_name, allow_not_found=True)
        if uid is None:
            uid, user_nickname = check_uid_with_user_nickname(agent, user_nickname, uid, schema2, table_name=table_name, allow_not_found=True)
    update_process_table(table_name, agent, user_nickname, uid, sets, allow_not_found=allow_not_found, schema2=schema2)
    return uid


def check_uid_with_user_nickname(agent, user_nickname, uid, schema2, table_name=None, allow_not_found=False):
    if table_name is None:
        table_name = greet_table_name
    if uid is None and user_nickname is not None and agent is not None:
        sql = f"SELECT uid,昵称 FROM {schema2}.{table_name} WHERE agent='{agent}' ORDER BY id DESC"
        results = query_sql(sql, schema2)
        for res in results:
            n = res['昵称']
            ni=0
            got = False
            for c in user_nickname:
                if is_invisible(c):
                    continue
                pos = n.find(c,ni)
                if pos<0:
                    got = False
                    break
                ni = pos+1
                got = True
            if got:
                uid = res['uid']
                user_nickname = n
        if uid is None:
            if allow_not_found:
                return None, user_nickname
            else:
                raise ValueError(f"在表【{schema2}.{table_name}】中没找到符合条件的数据：agent=【{agent}】，用户昵称【{user_nickname}】")
    return uid, user_nickname


def update_process_table(table_name, agent, user_nickname, uid, sets, schema2, allow_not_found=True):
    if uid in ['', None]:
        filters = {'agent': agent, '昵称': user_nickname}
    else:
        filters = {'agent': agent, 'uid': uid}
    if '留资' in sets:
        filters['留资'] = sets['留资']
    filter_str = get_filter_str(filters)
    sql = f"SELECT * FROM {schema2}.{table_name} WHERE {filter_str} ORDER BY id DESC LIMIT 1"
    res = query_sql(sql, schema2)
    if len(res)>0:
        for k in ['点赞状态','关注状态','打招呼状态','回复状态','留资','入库状态']:
            if k in sets and k in res[0] and sets[k]==res[0][k]:
                return
#                raise ValueError(f"状态重复设置：agent【{agent}】，用户昵称【{user_nickname}】，uid【{uid}】，{k}【{sets[k]}】")

        sql = f"UPDATE {schema2}.{table_name} SET "
        set_str = get_set_str(sets)
        if set_str == '':
            raise ValueError('无可更新的项')
        sql += set_str
        if filter_str != '':
            sql += f" WHERE " + filter_str
        updated_rows = execute_sql(sql, schema2)
        if updated_rows == 0:
            err = f"没找到符合条件的设备："+filter_str
            raise ValueError(err)
    else:
        if not allow_not_found:
            raise ValueError(f"没找到数据：agent={agent}, user_nickname={user_nickname}, uid={uid}")
        if agent is not None:
            sets['agent'] = agent
        if uid is not None:
            sets['uid'] = uid
        if user_nickname is not None:
            sets['昵称'] = user_nickname

        for k in ['点赞状态','关注状态','打招呼状态','回复状态','留资']:
            if k in sets:
                user_nickname2 = double_single_quotes(sets['昵称'])
                sql = f"SELECT * FROM {schema2}.{table_name} WHERE agent='{agent}' AND 昵称='{user_nickname2}' AND {k}='{sets[k]}' ORDER BY id DESC LIMIT 1"
                res2 = query_sql(sql, schema2)
                if len(res2)>0:
                    return
#                    raise ValueError(f"状态重复设置：agent【{agent}】，用户昵称【{sets['昵称']}】，{k}【{sets[k]}】")

        insert_str = get_insert_sql_str(sets)
        sql = f"INSERT INTO {schema2}.{table_name} {insert_str}"
        updated_rows = execute_sql(sql, schema2)
        if updated_rows == 0:
            err = f"没找到符合条件的设备："+filter_str
            raise ValueError(err)


def boce_submit_videolink(param, schema2):
    if schema2 is None:
        raise ValueError(f"未提供【biz】")
    param = param.copy()
    sets = split_items_from_param(param, ['视频链接','点赞','留言','收藏','分享','视频简介','视频发布时间'])
    if sets.get('视频链接', '') == '':
        raise ValueError('未提供【视频链接】')
    if len(param) > 0:
        raise ValueError(f"不支持参数{list(param.keys())}")

    sql = f"SELECT 留言 FROM {schema2}.视频链接 WHERE 视频链接='{sets['视频链接']}'"
    res = query_sql(sql, schema2)
    des = ''
    if len(res)>0:
        if res[0]['留言']<=int(sets['留言'])*0.5:
            sql = f"DELETE FROM {schema2}.视频链接 WHERE 视频链接='{sets['视频链接']}'"
            count = execute_sql(sql, schema2)
            des = '状态设置为【未分配】'
    sets['提交时间'] = datetime_str()
    sets['状态'] = '未分配'
    insert_str = get_insert_sql_str(sets)
    sql = f"INSERT INTO {schema2}.视频链接 {insert_str}"
    count = execute_sql(sql, schema2)
    return count, des


def boce_get_videolink_feedback(param, schema2):
    if schema2 is None:
        raise ValueError(f"未提供【biz】")
    param = param.copy()
    filters = split_items_from_param(param, ['视频链接'])
    sets = split_items_from_param(param, ['状态'])
    if filters.get('视频链接', '') == '':
        raise ValueError('未提供【视频链接】')
    if sets.get('状态', '') == '':
        raise ValueError('状态')
    if len(param) > 0:
        raise ValueError(f"不支持参数{list(param.keys())}")

    filter_str = get_filter_str(filters)
    insert_str = get_insert_sql_str(sets)
    sql = f"UPDATE {schema2}.视频链接 SET "+', '.join(f"{k}='{v}'" for k,v in sets.items())+f" WHERE {filter_str}"
    count = execute_sql(sql, schema2)
    return count


def boce_get_videolink(param, schema2):
    if schema2 is None:
        raise ValueError(f"未提供【biz】")
    if len(param) > 0:
        raise ValueError(f"不支持参数{list(param.keys())}")

    sql = f"SELECT 视频链接 FROM {schema2}.视频链接 WHERE 状态='未分配' order by 提交时间 desc limit 1"
    res = query_sql(sql, schema2)
    if len(res)==0:
        raise ValueError(f"{schema2}.视频链接，未找到【未分配】的记录】")

    sql = f"UPDATE {schema2}.视频链接 set 状态='已分配' where 视频链接='{res[0]['视频链接']}'"
    count = execute_sql(sql, schema2)
    return [res[0]['视频链接']]


def boce_submit_info(param, schema2):
    if schema2 is None:
        raise ValueError(f"未提供【biz】")
    param = param.copy()
    sets = split_items_from_param(param, ['抖音号','主页分享链接','评论索引','评论','评论时间','视频链接','性别','年龄','城市','IP属地'])
    if sets.get('抖音号', '') == '':
        raise ValueError('未提供【抖音号】')
    if sets.get('主页分享链接', '') == '':
        raise ValueError('未提供【主页分享链接】')
    if len(param) > 0:
        raise ValueError(f"不支持参数{list(param.keys())}")

    change_key(sets, '评论', '线索')
    change_key(sets, '抖音号', 'uid')
    change_key(sets, '评论时间', '咨询时间')
    sets['质检时间'] = datetime_str()
    insert_str = get_insert_sql_str(sets)
    sql = f"INSERT INTO {schema2}.{user_info_table_name} {insert_str}"
    count = execute_sql(sql, schema2)
    return count


def update_homepage_status(param, schema2):
    param = param.copy()
    if 'agent' not in param and 'agent_nickname' not in param:
        raise ValueError('[agent,agent_nickname] 至少要提供一项')
    if 'agent' in param and 'agent_nickname' in param:
        raise ValueError('[agent,agent_nickname] 至多要提供一项')
    if 'uid' not in param and '昵称' not in param:
        raise ValueError('[uid,nickname] 至少要提供一项')
    agent = split_item_from_param(param, 'agent')
    agent_nickname = split_item_from_param(param, 'agent_nickname')
    uid = split_item_from_param(param, 'uid')
    user_nickname = split_item_from_param(param, '昵称')
    sets = split_items_from_param(param, ['关注状态','点赞状态','打招呼状态','回复状态','留资','留资备注','入库状态','手机id','丢弃'])
    if sets.get('关注状态', '') not in like_types:
        raise ValueError('unknown like_type')
    if sets.get('打招呼状态', '') not in greet_types:
        raise ValueError('unknown greet_type')
    if sets.get('回复状态', '') not in reply_types:
        raise ValueError('unknown reply_type')
    got_liked = False
    if sets.get('关注状态',None) == '已关注':
        got_liked = True
    if len(param) > 0:
        raise ValueError(f"不支持参数{list(param.keys())}")

    if agent_nickname is not None:
        sql = f"SELECT 抖音号 FROM {device_table_name} WHERE 抖音昵称='{agent_nickname}'"
        res = query_sql(sql, schema2)
        if len(res)==0:
            raise ValueError(f"设备列表中没找到抖音昵称【{agent_nickname}】")
        agent = res[0]['抖音号']

    if uid is not None and user_nickname is None:
        sql = f"SELECT 昵称 FROM {schema2}.{user_info_table_name} WHERE uid='{uid}' ORDER BY 更新时间 DESC LIMIT 1"
        res = query_sql(sql, schema2)
        if len(res)==0:
            raise ValueError(f"没找到uid【{uid}】")
        user_nickname = res[0]['昵称']

    if sets.get('关注状态',None) is not None:
        sets2 = {'关注状态':sets['关注状态'],'关注时间':datetime_str()}
        update_with_user_nickname(guanzhu_table_name, agent, user_nickname, uid, sets2, schema2=schema2)
    if sets.get('点赞状态',None) is not None:
        sets2 = {'点赞状态':sets['点赞状态'],'点赞时间':datetime_str()}
        update_with_user_nickname(dianzan_table_name, agent, user_nickname, uid, sets2, schema2=schema2)
    if sets.get('打招呼状态',None) is not None:
        sets2 = {'打招呼状态':sets['打招呼状态'],'打招呼时间':datetime_str()}
        update_with_user_nickname(greet_table_name, agent, user_nickname, uid, sets2, schema2=schema2)
    if sets.get('回复状态',None) is not None:
        sets2 = {'回复状态':sets['回复状态'],'回复时间':datetime_str()}
        update_with_user_nickname(reply_table_name, agent, user_nickname, uid, sets2, schema2=schema2)
    if sets.get('留资',None) is not None:
        sets2 = {'留资':sets['留资'],'留资时间':datetime_str()}
        liuzi_note = sets.get('留资备注',None)
        if liuzi_note is not None:
            sets2['备注'] = liuzi_note
        uid = update_with_user_nickname(liuzi_table_name, agent, user_nickname, uid, sets2, schema2=schema2)
        if uid not in ['', None]:
            sql = f"INSERT IGNORE INTO {schema2}.{user_info_liuzi_table_name} SELECT * FROM {schema2}.{user_info_table_name} WHERE uid={uid}"
            execute_sql(sql, schema2)
    if sets.get('入库状态',None) is not None:
        sets2 = {'入库状态':sets['入库状态'],'入库时间':datetime_str()}
        update_with_user_nickname(liuzi_table_name, agent, user_nickname, uid, sets2, allow_not_found=False, schema2=schema2)
    if sets.get('丢弃',None) is not None:
        sql = f"UPDATE {schema2}.{user_info_table_name} SET 丢弃='{sets['丢弃']}' WHERE uid='{uid}'"
        execute_sql(sql, schema2)
        sets2 = {'打招呼状态':'打招呼失败'}
        update_with_user_nickname(greet_table_name, agent, user_nickname, uid, sets2, schema2=schema2)

    if got_liked:
        sql = f"UPDATE {device_table_name} SET 工作状态='正常',异常时间='',不能关注时间='' WHERE 抖音号='{agent}'"
        execute_sql(sql, schema2)
    return True


def split_num_from_arg(arg):
    num = 1
    if 'num' in arg:
        num = arg['num']
        if not num.isdigit():
            raise ValueError('cannot parse[num]')
        num = int(num)
        if num < 0 or num > 100:
            raise ValueError('[数量] out of range')
        if num == 0:
            num = 1000
        del arg['num']
    return num


def get_city_str(devices):
    cities = {}
    for r in devices:
        if r['任务地点'] not in cities:
            cities[r['任务地点']] = {}
        cities[r['任务地点']][r['性别']]=0
    city_str = ''
    for city in cities:
        for sex in cities[city]:
            if sex=='全部':
                if city in big_cities:
                    city_str += f" OR (城市 like '%{city}-{city}%' or 城市='{city}-')"
                else:
                    city_str += f" OR 城市 like '%{city}%'"
            else:
                if city in big_cities:
                    city_str += f" OR (性别='{sex}' AND (城市 like '%{city}-{city}%' or 城市='{city}-'))"
                else:
                    city_str += f" OR (性别='{sex}' AND 城市 like '%{city}%')"
    if city_str.startswith(' OR '):
        city_str = city_str[4:]
    return city_str


def filter_allocate_homepage(param, schema2):
    if schema2 is None:
        raise ValueError(f"未提供【biz】")
    param = param.copy()
    if len(param) > 0:
        raise ValueError(f"不支持参数{list(param.keys())}")

    sql = f"SELECT 任务地点,性别 FROM {device_table_name}"
    res = query_sql(sql, schema2)

    sql = f"SELECT {user_info_table_name}.uid,主页,{user_info_table_name}.昵称,城市,性别 FROM {schema2}.{user_info_table_name} LEFT JOIN {schema2}.{greet_table_name} ON {user_info_table_name}.uid={greet_table_name}.uid where {greet_table_name}.uid IS NULL AND 丢弃过滤='' AND 丢弃=''"
    city_str = get_city_str(res)
    sql += f" AND ({city_str})"
    sql += " order by 更新时间 desc limit 1"
    res = query_sql(sql, schema2)
    if len(res)==0:
        raise ValueError(f"没有符合条件的未过滤用户")

    sql = f"UPDATE {schema2}.{user_info_table_name} SET 丢弃过滤='进行' where uid='{res[0]['uid']}'"
    count = execute_sql(sql, schema2)

    return True, res


def filter_update_homepage(param, schema2):
    if schema2 is None:
        raise ValueError(f"未提供【biz】")
    param = param.copy()
    uid = split_item_from_param(param, 'uid')
    abandon = split_item_from_param(param, '丢弃')
    if len(param) > 0:
        raise ValueError(f"不支持参数{list(param.keys())}")

    sql = f"UPDATE {schema2}.{user_info_table_name} SET 丢弃过滤='完成', 过滤时间='{datetime_str()}', 丢弃='{abandon}' where uid='{uid}'"
    updated_rows = execute_sql(sql, schema2)
    return True


def recheck_allocate_homepage(param, schema2):
    if schema2 is None:
        raise ValueError(f"未提供【biz】")
    param = param.copy()
    num = split_item_from_param(param, 'num')
    city = split_item_from_param(param, '城市')
    filters = split_items_from_param(param, ['性别'])
    filters['复检']=''
    filters['丢弃']=''
    sex = filters.get('性别')
    if sex not in ['男','女',None]:
        raise ValueError(f"sex只能填【男、女】")
    if num is None:
        num = 1
    if len(param) > 0:
        raise ValueError(f"不支持参数{list(param.keys())}")

    sql = f"SELECT 主页,{user_info_table_name}.uid,{user_info_table_name}.昵称,年龄,性别,城市,IP属地,线索,更新时间 FROM {schema2}.{user_info_table_name}"
    filter_str = get_filter_str(filters)
    if city is not None:
        if city in big_cities:
            filter_str += f" AND (城市 like '%{city}-{city}%' or 城市='{city}-')"
        else:
            filter_str += f" AND 城市 like '%{city}%'"
    sql += f" LEFT JOIN {schema2}.{greet_table_name} ON {user_info_table_name}.uid=打招呼.uid WHERE 打招呼.uid IS NULL"
    if filter_str!='':
        sql += ' AND ' + filter_str
    sql += f" order by 更新时间 desc limit {num}"
    res = query_sql(sql, schema2)

    return True, res


def recheck_update_homepage(param, schema2):
    if schema2 is None:
        raise ValueError(f"未提供【biz】")
    param = param.copy()
    uid = split_item_from_param(param, 'uid')
    score = split_item_from_param(param, 'score')
    if uid is None:
        raise ValueError(f"没提供 uid")
    if score is None:
        raise ValueError(f"没提供 score")
    if len(param) > 0:
        raise ValueError(f"不支持参数{list(param.keys())}")

    sql = f"UPDATE {schema2}.{user_info_table_name} SET 复检='{score}', 复检时间='{datetime_str()}' where uid='{uid}'"
    updated_rows = execute_sql(sql, schema2)

    return True


def query_liuzi_info(param, schema2):
    param = param.copy()
    nickname = split_item_from_param(param, '昵称')
    agent_nickname = split_item_from_param(param, 'agent_nickname')
    if nickname is None:
        raise ValueError(f"没提供 nickname")
    if agent_nickname is None:
        raise ValueError(f"没提供 agent_nickname")
    if len(param) > 0:
        raise ValueError(f"不支持参数{list(param.keys())}")

    sql = f"SELECT 抖音号 FROM {device_table_name} WHERE 抖音昵称='{agent_nickname}'"
    res = query_sql(sql, schema2)
    if len(res)==0:
        raise ValueError(f"设备列表没有抖音昵称：{agent_nickname}")

    agent = res[0]['抖音号']

    uid, user_nickname = check_uid_with_user_nickname(agent, nickname, None, schema2, greet_table_name, allow_not_found=True)
    if uid is None:
        uid, user_nickname = check_uid_with_user_nickname(agent, nickname, None, schema2, dianzan_table_name, allow_not_found=True)
        if uid is None:
            uid, user_nickname = check_uid_with_user_nickname(agent, nickname, None, schema2, liuzi_table_name)
            if uid is None:
                raise ValueError(f"没有此人的留资信息")
            elif uid=='':
                raise ValueError(f"有此人的留资信息，没有用户信息")

    sql = f"SELECT 年龄,性别,城市,线索 FROM {schema2}.{user_info_liuzi_table_name} WHERE uid='{uid}'"
    res = query_sql(sql, schema2)

    if len(res) == 0:
        raise ValueError(f"没找到符合条件的用户，agent_nickname【{agent_nickname}】，nickname【{nickname}】")
    return True, res


def query_liuzi_info2(param, schema2):
    param = param.copy()
    city = split_item_from_param(param, '城市')
    if len(param) > 0:
        raise ValueError(f"不支持参数{list(param.keys())}")

    sql = f"SELECT 留资.留资时间,留资.昵称,留资.入库状态,device.抖音昵称 FROM {schema2}.{liuzi_table_name} left join {schema2}.{user_info_table_name} on 留资.uid={user_info_table_name}.uid left join {device_table_name} on {liuzi_table_name}.agent={device_table_name}.抖音号 where 城市 like '%{city}%' order by 留资时间 desc"
    res = query_sql(sql, schema2)
    res2 = []
    for r in res:
        res2.append({'留资时间':r['留资时间'],'用户昵称':r['昵称'],'入库状态':r['入库状态'],'工作昵称':r['抖音昵称']})
    return True, res2


def query_homepage_status(param, schema2):
    param = param.copy()
    city = split_item_from_param(param, '城市')
    filters = split_items_from_param(param, ['主页','uid','昵称','年龄','性别','质检'])
    select_str = split_item_from_param(param, 'select_str')
    if select_str is None:
        select_str = '*'
    num = split_num_from_arg(param)
    if len(param) > 0:
        raise ValueError(f"不支持参数{list(param.keys())}")
    if select_str=='':
        select_str='*'

    sql = f"SELECT {select_str} FROM {schema2}.{user_info_table_name}"
    filter_str = get_filter_str(filters)
    if filter_str.startswith(' AND '):
        filter_str = filter_str[5:]
    if filter_str!='':
        sql += ' WHERE ' + filter_str
    if city is not None:
        if city in big_cities:
            sql2 = f" AND (城市 like '%{city}-{city}%' or 城市='{city}-')"
        else:
            sql2 = f" AND 城市 like '%{city}%'"
        if 'WHERE' in sql:
            sql += sql2
        else:
            sql += ' WHERE' + sql2[4:]
    sql += f" ORDER BY 咨询时间 DESC LIMIT {num}"
    res = query_sql(sql, schema2)

    return True, res


def get_hour_minute_from_str(time_str):
    try:
        time_str = time_str.replace('：', ':')
        start_time = datetime.datetime.strptime(time_str, '%H:%M')
        return start_time
    except:
        pass
    return None


def try_login(url, account, password, pre_schema):
    sql = f"SELECT * FROM {pre_schema}common.user WHERE 用户名='{account}'"
    res = query_sql(sql)
    if len(res)==0:
        raise ValueError("登陆失败")
    if res[0]['密码'] != password:
        raise ValueError("登陆失败")

    sql = f"SELECT * FROM {pre_schema}common.logged_in_url WHERE url='{url}'"
    res = query_sql(sql)
    if len(res)==0:
        sets = {'url':url,'用户名':account}
        insert_str = get_insert_sql_str(sets)
        sql = f"INSERT INTO {pre_schema}common.logged_in_url {insert_str}"
        count = execute_sql(sql)
        if count==0:
            raise ValueError(f"登录入库失败")
    else:
        sql = f"UPDATE {pre_schema}common.logged_in_url SET 用户名='{account}' where url='{url}'"
        count = execute_sql(sql)
        if count==0:
            raise ValueError(f"登录入库更新失败")


def try_logout(url, pre_schema):
    sql = f"DELETE FROM {pre_schema}common.logged_in_url WHERE url='{url}'"
    count = execute_sql(sql)


def update_device(info, schema2):
    updated_names = ''
    updated_num = 0
    param = info['param']
    for k in list(param.keys()):
        if param[k]=='':
            del param[k]
    # 如果是设置手机信息，则只允许设置一台手机，不允许批量设置
    the_type = info['param']['type']
    del info['param']['type']

    if the_type in ['set_device']:
        for device in info['devices']:
            douyinhao = device['抖音号']
            select = device.get('select', None)
            if select is not True:
                continue
            value = param.get('value','')
            sql = f"UPDATE {device_table_name} SET {param['sign']}='{value}'"
            sql += f" WHERE 抖音号='{douyinhao}'"
            count = execute_sql(sql, schema2)
            updated_names += f"【{device['抖音昵称']}】"
            updated_num += 1


    if the_type in ['start','stop']:
        for device in info['devices']:
            douyinhao = device['抖音号']
            select = device.get('select', None)
            if select is not True:
                continue
            sql = f"SELECT * FROM {device_table_name} WHERE 抖音号='{douyinhao}'"
            res = query_sql(sql, schema2)
            if res == []:
                raise ValueError(f"没找到 抖音号【{douyinhao}】")

            if the_type=='start':
                s='运行'
            if the_type=='stop':
                s='停止'
            sql = f"UPDATE {device_table_name} SET 运行命令='{s}'"
            sql += f" WHERE 抖音号='{douyinhao}'"
            count = execute_sql(sql, schema2)
            updated_names += f"【{device['抖音昵称']}】"
            updated_num += 1

    if the_type == 'update_phone':
        selected = 0
        for device in info['devices']:
            select = device.get('select', None)
            if select is True:
                selected += 1
        if selected>1:
            raise ValueError(f"不能批量设置手机配置")

    if the_type == 'update_task':
        if info['param'].get('任务地点') == '':
            raise ValueError(f"任务地点不能为空")
        if info['param'].get('是否点赞头像') not in [None, '是', '否']:
            raise ValueError(f"格式不对：是否点赞头像。可选项：是,否")

    if the_type in ['update_task', 'update_phone']:
        for device in info['devices']:
            select = device.get('select', None)
            if select is not True:
                continue
            douyinhao = device['抖音号']
            sql = f"SELECT * FROM {device_table_name} WHERE 抖音号='{douyinhao}'"
            res = query_sql(sql, schema2)
            if res==[]:
                raise ValueError(f"没找到手机【{douyinhao}】")

            sql = f"UPDATE {device_table_name} SET "
            set_sql = ''

            if '性别' in param:
                if param['性别'] not in ['男','女','全部']:
                    raise ValueError('格式不对：性别。可选项：男,女,全部')
            if '每日关招数' in param:
                try:
                    if int(param['每日关招数'])<=0:
                        raise ValueError('格式不对：每日关招数')
                except:
                    raise ValueError('格式不对：每日关招数')
            start_time, end_time = None, None
            if '每日关招开始时间' in param:
                try:
                    start_time = get_hour_minute_from_str(param['每日关招开始时间'])
                except:
                    raise ValueError('格式不对：每日关招开始时间')
                if start_time is None:
                    raise ValueError('格式不对：每日关招开始时间')
            if '每日关招结束时间' in param:
                try:
                    end_time = get_hour_minute_from_str(param['每日关招结束时间'])
                except:
                    raise ValueError('格式不对：每日关招结束时间')
                if end_time is None:
                    raise ValueError('格式不对：每日关招结束时间')
            if start_time is not None and end_time is not None and end_time<=start_time:
                raise ValueError('每日关招开始时间 和 每日关招结束时间 不匹配')
            if '关招间隔分钟' in param:
                try:
                    if int(param['关招间隔分钟'])<=0:
                        raise ValueError('格式不对：关招间隔分钟')
                except:
                    raise ValueError('格式不对：关招间隔分钟')
            if '关注停则招呼停' in param:
                if param['关注停则招呼停'] not in [True, False]:
                    raise ValueError('格式不对：关注停则招呼停')

            if '关注停则招呼停' in param:
                if param['关注停则招呼停']==True:
                    param['关注停则招呼停'] = '是'
                else:
                    param['关注停则招呼停'] = '否'
            for k in param:
                set_sql += f", {k}='{param[k]}'"
            sql += set_sql[2:]
            sql += f" WHERE 抖音号='{douyinhao}'"
            count = execute_sql(sql, schema2)
            updated_names += f"【{device['抖音昵称']}】"
            updated_num += 1

    if the_type == 'remove_phone':
        selected = 0
        the_device = None
        for device in info['devices']:
            select = device.get('select', None)
            if select is True:
                selected += 1
                the_device = device
        if selected>1:
            raise ValueError(f"不能批量注销手机")
        douyinhao = split_item_from_param(info['param'], '抖音号')
        if douyinhao is None:
            raise ValueError('没提供【抖音号】')

        sql = f"DELETE FROM {device_table_name} WHERE 抖音号='{douyinhao}'"
        count = execute_sql(sql, schema2)
        updated_names += f"【{the_device['抖音昵称']}】"
        updated_num += 1

    return updated_num, updated_names


def update_biz(info):
    updated_names = ''
    updated_num = 0
    param = info['param']
    for k in list(param.keys()):
        if param[k]=='':
            del param[k]
    # 如果是设置手机信息，则只允许设置一台手机，不允许批量设置
    the_type = info['param']['type']
    del info['param']['type']

    if the_type in ['set_biz']:
        for device in info['devices']:
            douyinhao = device['抖音号']
            select = device.get('select', None)
            if select is not True:
                continue
            value = param.get('value','')
            sql = f"UPDATE {device_table_name} SET {param['sign']}='{value}'"
            sql += f" WHERE 抖音号='{douyinhao}'"
            count = execute_sql(sql, logging=False)
            updated_names += f"【{device['抖音昵称']}】"
            updated_num += 1

    return updated_num, updated_names


def device_heartbeat(param, schema2):
    param = param.copy()
    phone_id = split_item_from_param(param, '手机id')
    script_version = split_item_from_param(param, '脚本版本')
    general_version = split_item_from_param(param, '总版本')
    if phone_id is None:
        raise ValueError('[phone_id] not provided')
    if len(param) > 0:
        raise ValueError(f"不支持参数{list(param.keys())}")
    sql = f"SELECT * FROM {device_table_name} WHERE 手机id='{phone_id}'"
    res = query_sql(sql, schema2,logging=False)
    if len(res)==0:
        raise ValueError(f"没找到手机id为【{phone_id}】的设备")
    sql = f"UPDATE {device_table_name} SET 上次手机心跳时间='{datetime_str()}'"
    if script_version is not None:
        sql += f", 脚本版本='{script_version}'"
    if general_version is not None:
        sql += f", 总版本='{general_version}'"
    sql += f" WHERE 手机id='{phone_id}'"
    updated_rows = execute_sql(sql, schema2,logging=False)
    if updated_rows==0:
        raise ValueError(f"没更新手机心跳")

    return res


def gpt_heartbeat(param, schema2):
    param = param.copy()
    nickname = split_item_from_param(param, '昵称')
    if nickname is None:
        raise ValueError('[nickname] not provided')
    if len(param) > 0:
        raise ValueError(f"不支持参数{list(param.keys())}")
    sql = f"SELECT * FROM {device_table_name} WHERE 抖音昵称='{nickname}'"
    res = query_sql(sql, schema2,logging=False)
    if len(res)==0:
        raise ValueError(f"没找到抖音昵称为【{nickname}】的设备")
    sql = f"UPDATE {device_table_name} SET 上次GPT心跳时间='{datetime_str()}'"
    sql += f" WHERE 抖音昵称='{nickname}'"
    updated_rows = execute_sql(sql, schema2,logging=False)
    if updated_rows==0:
        raise ValueError('没更新gpt心跳')

    return res


def device_status(param, schema2):
    param = param.copy()
    phone_id = split_item_from_param(param, '手机id')
    work_status = split_item_from_param(param, '工作状态')
    if phone_id is None:
        raise ValueError('[phone_id] not provided')
    if len(param) > 0:
        raise ValueError(f"不支持参数{list(param.keys())}")
    sql = f"SELECT * FROM {device_table_name} WHERE 手机id='{phone_id}'"
    res = query_sql(sql, schema2,logging=False)
    if len(res)==0:
        raise ValueError(f"没找到手机id为【{phone_id}】的设备")
    sql = f"UPDATE {device_table_name} SET 工作状态='{work_status}'"
    if work_status!='正常':
        sql += f", 异常时间='{datetime_str()}'"
    if work_status=='无法关注':
        sql += f", 不能关注时间='{datetime_str()}'"
    sql += f" WHERE 手机id='{phone_id}'"
    updated_rows = execute_sql(sql, schema2, logging=False)
#        if updated_rows==0:
#            raise ValueError('没更新设备工作状态')

    return res


def device_get_task(param, schema2):
    param = param.copy()
    agent = split_item_from_param(param, 'agent')
    if agent is None:
        raise ValueError('[agent] not provided')
    if len(param) > 0:
        raise ValueError(f"不支持参数{list(param.keys())}")
    sql = f"SELECT * FROM {device_table_name} WHERE 抖音号='{agent}'"
    results = query_sql(sql, schema2)
    if len(results)==0:
        raise ValueError(f"没找到抖音号为【{agent}】的设备")
    for res in results:
        to_like_avatar, to_like, to_greet = is_it_time_to_greet(agent, schema2)
        res['该点赞了'] = to_like_avatar
        res['该关注了'] = to_like
        res['该招呼了'] = to_greet

    return results


def device_info_modify(param, schema2):
    param = param.copy()
    douyinhao = split_item_from_param(param, '抖音号')
    type = split_item_from_param(param, 'type')
    sets = split_items_from_param(param, ['手机名称','手机型号','手机id','uid','抖音昵称','登陆邮箱','登陆邮箱密码','实名认证人','电话','远控地址','工作状态','内网ip'])
    if douyinhao is None:
        raise ValueError('[抖音号] not provided')
    if type is None:
        raise ValueError('[type] not provided')
    if len(param) > 0:
        raise ValueError(f"不支持参数{list(param.keys())}")
    sql = f"SELECT * FROM {device_table_name} WHERE 抖音号='{douyinhao}'"
    ret = query_sql(sql, schema2)
    record_exist = len(ret)>0
    if type == '增':
        if record_exist:
            raise ValueError(f"抖音号[{douyinhao}]已经存在")
        sets['抖音号'] = douyinhao
        if '运行命令' not in sets:
            sets['运行命令'] = '运行'
        if '工作状态' not in sets:
            sets['工作状态'] = '正常'
        insert_str = get_insert_sql_str(sets)
        sql = f"INSERT INTO {device_table_name} {insert_str}"
    elif type == '改':
        if record_exist:
            if len(sets) == 0:
                raise ValueError('无可更新的数据')
            if sets.get('工作状态', '正常') != '正常':
                sets['异常时间'] = datetime_str()
            sql = f"UPDATE {device_table_name} SET "+', '.join(f"{k}='{v}'" for k,v in sets.items())+f" WHERE 抖音号='{douyinhao}'"
        else:
            sets['抖音号'] = douyinhao
            if '运行命令' not in sets:
                sets['运行命令'] = '运行'
            if '工作状态' not in sets:
                sets['工作状态'] = '正常'
            insert_str = get_insert_sql_str(sets)
            sql = f"INSERT INTO {device_table_name} {insert_str}"
    elif type == '删':
        if not record_exist:
            raise ValueError(f"抖音号[{douyinhao}]不存在")
        sql = f"DELETE FROM {device_table_name} WHERE 抖音号='{douyinhao}'"
    else:
        raise ValueError(f"unknown type [{type}]")
    count = execute_sql(sql, schema2)

    return True


def execute_sql(sql, schema2=None, logging=True):
    while True:
        try:
            conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            cursor = conn.cursor()
            if logging:
                print_sql(sql, schema2)
            cursor.execute(sql)
            updated_rows = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()
            return updated_rows

        except Exception as e:
            cursor.close()
            conn.close()
            raise ValueError(str(e))


def query_sql(sql, biz=None, logging=True):
    conn, cursor = connect_to_db()
    try:
        if logging:
            print_sql(sql, biz)
        cursor.execute(sql)
        # 获取查询结果
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        columns = [column[0] for column in cursor.description]
        result_dict_list = [dict(zip(columns, row)) for row in result]
    except Exception as e:
        conn_cursor_exception(conn, cursor, e)

    return result_dict_list


def insert_user_info(infos, schema2, table_name=None):
    if table_name is None:
        table_name = user_info_table_name
    while True:
        try:
            columns = get_table_columns(table_name=table_name, logging=False, schema2=schema2)

            conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            cursor = conn.cursor()

            print(f"开始写数据库 {len(infos)} 条")
            for i in range(len(infos)):
                if i>0 and i % 10000 == 0:
                    print(f"写了 {i} 条")
                info=infos[i]
                info = info.copy()
                keys2 = list(info.keys())
                for k in keys2:
                    if k not in columns or info[k] == None:
                        del info[k]
                        continue
                    if columns[k]['Type'].startswith('varchar'):
                        if info[k] is None:
                            info[k] = ''
                        info[k] = info[k][:columns[k]['len']]
                    elif columns[k]['Type']=='int':
                        if info[k]=='':
                            del info[k]
                            continue
                        else:
                            try:
                                info[k] = int(info[k])
                            except:
                                del info[k]
                                continue

                insert_str = get_insert_sql_str(info)
                sql = f"INSERT IGNORE INTO {schema2}.{table_name} {insert_str}"

                cursor.execute(sql)

#                execute_sql(sql, schema2, logging=False)
            conn.commit()
            cursor.close()
            conn.close()
            break
        except Exception as e:
            print(e)


def get_table_columns(table_name, schema2, logging=True):
    # 执行 SQL 查询以获取表的列信息
    sql = f"DESCRIBE {schema2}.{table_name}"
    columns = query_sql(sql, schema2, logging)
    # 打印列信息
    ret = {}
    for column in columns:
        if column['Type'].startswith('varchar'):
            column['len'] = int(column['Type'][8:-1])
            column['Type'] = 'varchar'
        ret[column['Field']] = column
    return ret


def get_newest_unfilled_user_info_and_set_status(info_extractor):
    while True:
        try:
            conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            cursor = conn.cursor()
            sql = f"SELECT * FROM {user_info_table_name} WHERE 提取信息='否' OR 提取信息='进行' AND 提取信息者='{info_extractor}' ORDER BY 咨询时间 DESC LIMIT 1"
            cursor.execute(sql)
            # 获取查询结果
            result = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            result_dict_list = [dict(zip(columns, row)) for row in result]
            suc = False
            if len(result)>0:
                result_dict_list[0]['提取信息者'] = info_extractor
                sql = f"UPDATE {user_info_table_name} SET 提取信息='进行', 提取信息者='{info_extractor}' WHERE 主页 = '{result_dict_list[0]['主页']}'"
                cursor.execute(sql)
                conn.commit()
                suc=True
            cursor.close()
            conn.close()
            break
        except Exception as e:
            cursor.close()
            conn.close()
            print(e)

    return suc, result_dict_list


def get_time_len_str(last_time):
    if last_time==0:
        return 'N/A', -1
    minutes = int((datetime.datetime.now() - last_time).total_seconds() / 60)
    total_minutes = minutes
    hours = int(minutes / 60)
    minutes -= hours * 60
    time_len_str = f"{minutes}分钟"
    if hours > 0:
        time_len_str = f"{hours}小时" + time_len_str
    return time_len_str, total_minutes


def is_it_time_to_greet(agent, schema2):
    current_datetime = datetime.datetime.now()
    sql = f"SELECT * FROM {device_table_name} WHERE 抖音号='{agent}' order by 任务地点"
    ret = query_sql(sql, schema2)
    if ret == []:
        raise ValueError(f"没找到抖音号为【{agent}】的设备")
    l = ret[0]

    l['该点赞了'] = l['是否点赞头像']

    for k in l:
        if l[k] is None:
            l[k] = ''

    dates=[]
    days = 5
    for i in range(days):
        dates.append(date_str(-i))

    sql = f"SELECT * FROM {schema2}.{greet_table_name} WHERE 打招呼状态='已打招呼' AND 打招呼时间>'{dates[-1]}'"
    ret2 = query_sql(sql, schema2)

    greet_done = np.zeros(days, dtype=int)
    post_like_greet_num = 0
    try:
        unable_like_time = datetime.datetime.strptime(l['不能关注时间'], '%Y-%m-%d %H:%M:%S')
        l['不能关注了'] = '是'
    except:
        unable_like_time = 0
        l['不能关注了'] = '否'
    unable_like_time_str,unable_like_minutes = get_time_len_str(unable_like_time)
    last_greet = ''
    for l2 in ret2:
        if l2['agent']==l['抖音号']:
            for i in range(days):
                if l2['打招呼时间'] >= dates[i] and (i<=0 or l2['打招呼时间'] < dates[i - 1]):
                    greet_done[i] += 1
            last_greet = max(last_greet, l2['打招呼时间'])
            try:
                ttt = datetime.datetime.strptime(l2['打招呼时间'], '%Y-%m-%d %H:%M:%S')
                greet_time_str,greet_minutes = get_time_len_str(ttt)
            except:
                continue
            if greet_minutes < unable_like_minutes:
                post_like_greet_num += 1

    last_greet_time = 0
    try:
        last_greet_time = datetime.datetime.strptime(last_greet, '%Y-%m-%d %H:%M:%S')
    except:
        pass
    l['该关注了'] = '否'
    l['该招呼了'] = '否'
    start_time_str = l['每日关招开始时间']
    if last_greet_time==0:
        start_time = get_hour_minute_from_str(start_time_str)
        try:
            time_from_string = datetime.datetime(current_datetime.year, current_datetime.month,
                                                 current_datetime.day,
                                                 start_time.hour, start_time.minute)
            if time_from_string <= current_datetime:
                l['该关注了'] = '是'
                l['该招呼了'] = '是'
        except:
            pass
    else:
        try:
            new_time = last_greet_time + datetime.timedelta(minutes=int(l['关招间隔分钟']))
            if new_time <= current_datetime:
                l['该关注了'] = '是'
                l['该招呼了'] = '是'
        except:
            pass

    unable_like_post_greet_num = 10000
    try:
        unable_like_post_greet_num = int(l['不能关注后打招呼数'])
    except:
        pass
    unable_like_recover_time = 0
    try:
        unable_like_recover_time = datetime.datetime.strptime(l['不能关注恢复时间'], '%H:%M')
    except:
        try:
            unable_like_recover_time = datetime.datetime.strptime(l['不能关注恢复时间'], '%H')
        except:
            pass
    recovered = False
    if unable_like_recover_time==0:
        unable_like_post_greet_num = 10000
    if unable_like_time==0:
        unable_like_post_greet_num = 10000
    else:
        try:
            unable_like_recover_delta = datetime.timedelta(hours=unable_like_recover_time.hour, minutes=unable_like_recover_time.minute)
            new_time = unable_like_time + unable_like_recover_delta
            if new_time <= datetime.datetime.now():
                recovered = True
                l['不能关注了'] = '否'
        except:
            pass
    if l['不能关注了']=='是':
        l['该关注了'] = '否'
    if post_like_greet_num>=unable_like_post_greet_num and not recovered:
        l['该关注了'] = '否'
        l['该招呼了'] = '否'
    if l['运行命令']=='停止':
        l['该关注了'] = '否'
        l['该招呼了'] = '否'

    end_time_str = l['每日关招结束时间']
    end_time = get_hour_minute_from_str(end_time_str)
    try:
        time_from_string = datetime.datetime(current_datetime.year, current_datetime.month,
                                             current_datetime.day,
                                             end_time.hour, end_time.minute)
        if time_from_string <= current_datetime:
            l['该关注了'] = '否'
            l['该招呼了'] = '否'
    except:
        pass

    return l['该点赞了'], l['该关注了'], l['该招呼了']


def batch_query(param, schema2):
    if schema2 is None:
        raise ValueError(f"未提供【biz】")
    start_time = split_item_from_param(param, 'start_time')
    end_time = split_item_from_param(param, 'end_time')
    time_type = split_item_from_param(param, 'time_type')
    if time_type not in ['更新时间','挖掘时间','质检时间','复检时间',None]:
        raise ValueError(f"time_type not in 【更新时间，挖掘时间，质检时间，复检时间】")
    if start_time is None:
        raise ValueError('[start_time] not provided')
    if end_time is None:
        raise ValueError('[end_time] not provided')
    if len(param) > 0:
        raise ValueError(f"不支持参数{list(param.keys())}")
    if time_type is None:
        time_type = '更新时间'
    sql = f"SELECT {user_info_table_name}.uid,城市,丢弃过滤,丢弃,过滤时间,复检,复检时间,打招呼状态,打招呼时间,回复状态,回复时间,留资,留资时间,{greet_table_name}.agent as '打招呼.agent',{reply_table_name}.agent as '回复.agent',{liuzi_table_name}.agent as '留资.agent' FROM {schema2}.{user_info_table_name} left join {schema2}.{greet_table_name} on {user_info_table_name}.uid={greet_table_name}.uid left join {schema2}.{reply_table_name} on {user_info_table_name}.uid={reply_table_name}.uid left join {schema2}.{liuzi_table_name} on {user_info_table_name}.uid={liuzi_table_name}.uid "
    sql += f"where {time_type}>='{start_time}' and {time_type}<'{end_time}'"
    ret = query_sql(sql, schema2)
    return ret


def query_uid_ip(param, schema2):
    param = param.copy()
    agent_nickname = split_item_from_param(param, 'agent_nickname')
    user_nickname = split_item_from_param(param, '昵称')
    if len(param) > 0:
        raise ValueError(f"不支持参数{list(param.keys())}")

    sql = f"SELECT 抖音号,内网ip FROM {device_table_name} WHERE 抖音昵称='{agent_nickname}'"
    res = query_sql(sql, schema2)
    if len(res)==0:
        raise ValueError(f"设备列表中没找到抖音昵称【{agent_nickname}】")
    agent = res[0]['抖音号']

    uid, user_nickname = check_uid_with_user_nickname(agent, user_nickname, None, schema2, table_name=greet_table_name)

    return {'uid':uid,'内网ip':res[0]['内网ip']}


def get_insert_sql_str(sets):
    sets2 = sets.copy()
    keys = ', '.join(sets2.keys())
    values = ', '.join(f"'{v}'" for v in sets2.values())
    sql = f"({keys}) VALUES ({values})"
    return sql


def get_cursor():
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    cursor = conn.cursor()
    return conn, cursor


def release_cursor(conn, cursor):
    conn.commit()
    cursor.close()
    conn.close()
