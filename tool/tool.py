import os, csv, pickle, time, datetime, openpyxl, json, threading, shutil, subprocess


def send_email(title='', content='', email=None):
    if email is None:
        print("未提供email")
        return
    # 连接到SMTP服务器并发送邮件
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.header import Header

        mail_host = "smtp.163.com"  # 设置服务器
        mail_user = "muforios@163.com"  # 用户名
        mail_pass = "JPKCHZXCXVSPJYBC"  # 授权码，注意不是邮箱登录密码，是上述设置的授权密码！！！
        sender = 'muforios@163.com'
        receivers = email  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

        message = MIMEText(str(content), 'plain', 'utf-8')
        message['From'] = "muforios@163.com"
        message['To'] = email
        subject = str(title)
        message['Subject'] = Header(subject, 'utf-8')
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host, 25)
        smtpObj.set_debuglevel(1)
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("邮件发送成功")
    except Exception as e:
        print("Error:", e)


def get_datetime_str():
    current_datetime = datetime.datetime.now()
    return current_datetime.strftime("%Y-%m-%d %H:%M:%S")


def get_date_str():
    current_datetime = datetime.datetime.now()
    return current_datetime.strftime("%Y-%m-%d")


def change_key(infos, src, dst):
    if type(infos)==dict:
        if src in infos:
            infos[dst] = infos[src]
            del infos[src]
    elif type(infos)==list:
        for info in infos:
            if src in info:
                info[dst] = info[src]
                del info[src]
    else:
        raise ValueError(f"change_key(), type error")


def get_chrome_exe_path():
    # 尝试从系统环境变量中获取Chrome可执行文件路径
    chrome_path = shutil.which("chrome.exe")

    # 如果在环境变量中找不到，尝试通过注册表查找
    if chrome_path is None:
        try:
            # Windows注册表中Chrome的默认安装路径
            reg_query_command = 'reg query "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\chrome.exe" /v Path'
            output = subprocess.check_output(reg_query_command, shell=True, stderr=subprocess.DEVNULL, text=True)

            # 从注册表输出中提取路径
            lines = output.splitlines()
            if len(lines) > 2:
                chrome_path = lines[2].split("    ")[-1].strip()
        except Exception as e:
            print(f"Error accessing registry: {e}")

    return chrome_path + "\\chrome.exe"


def thread_get_addr(driver, addr):
    driver.get(addr)


def _thread_input():
    input("按回车键继续")


def wait_for_input(minutes=1):
    print('等待%.2f分钟，继续'%(minutes))
    input_thread = threading.Thread(target=_thread_input)
    input_thread.daemon = True  # 设置为守护线程
    input_thread.start()
    input_thread.join(timeout=minutes * 60)
    print('\n等待结束，继续')


def _thread_get_addr(driver, addr):
    driver.get(addr)


def limit_time_get_addr(seconds, driver, addr):
    input_thread = threading.Thread(target=_thread_get_addr, args=(driver, addr))
    input_thread.daemon = True  # 设置为守护线程
    input_thread.start()
    input_thread.join(timeout=seconds)


def datetime_str(off_minutes=0):
    the_datetime = datetime.datetime.now()+datetime.timedelta(minutes=off_minutes)
    return the_datetime.strftime("%Y-%m-%d %H:%M:%S")


def date_str(off_days=0):
    current_datetime = datetime.datetime.now()+datetime.timedelta(days=off_days)
    return current_datetime.strftime("%Y-%m-%d")


def time_str():
    current_datetime = datetime.datetime.now()
    return current_datetime.strftime("%H:%M:%S")


def load_setting(fn):
    setting = {}
    if not os.path.exists(fn):
        return setting
    with open(fn, 'r') as f:
        setting = json.load(f)
        return setting


def replace_str_of_dictionary(infos, src, dst):
    for info in infos:
        for k in info:
            v = info[k]
            if type(v) == str:
                info[k] = v.replace(src, dst)


def add_line_to_file(fn, line):
    with open(fn, "a", encoding='utf-8-sig') as file:
        if not line.endswith('\n'):
            line += '\n'
        file.write(line)


def add_val_to_line(line, features, key):
    line += ','
    if key in features:
        line += str(features[key])
    return line


def add_keys_to_xls_sheet(sheet, keys):
    for i in range(len(keys)):
        sheet.cell(row=1, column=i + 1, value=keys[i])


def add_line_to_xls_sheet(sheet, keys, data):
    row = sheet.max_row + 1
    for i in range(len(keys)):
        if keys[i] not in data:
            continue
        sheet.cell(row=row, column=i + 1, value=data[keys[i]])
        #sheet.write(row, i, data[keys[i]])


def add_keys_to_file(fn, keys):
    ext = os.path.splitext(fn)[-1].lower()
    if ext=='.xlsx':
        add_keys_to_xls_file(fn, keys)
    elif ext=='.csv':
        add_keys_to_csv_file(fn, keys)
    else:
        raise '不支持的扩展名'


def add_keys_to_xls_file(fn, keys):
    if not os.path.exists(fn):
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        add_keys_to_xls_sheet(sheet, keys)
        workbook.save(fn)


def add_keys_to_csv_file(fn, keys):
    if not os.path.exists(fn):
        with open(fn, 'w', encoding='utf-8') as f:
            s = str(keys).replace('\'','').replace(' ','')[1:-1]
            f.write(s+'\n')


def add_line_to_file(fn, keys, data):
    ext = os.path.splitext(fn)[-1].lower()
    if ext=='.xlsx':
        add_line_to_xls_file(fn, keys, data)
    elif ext=='.csv':
        add_line_to_csv_file(fn, keys, data)
    else:
        raise '不支持的扩展名'


def add_line_to_csv_file(fn, keys, data):
    if not os.path.exists(fn):
        add_keys_to_csv_file(fn, keys)
    s=''
    for i in range(len(keys)):
        k = keys[i]
        if k in data:
            s+=str(data[k])
        if i+1<len(keys):
            s+=','
    print(s)
    with open(fn, 'a', encoding='utf-8') as f:
        f.write(s+'\n')


def add_line_to_xls_file(fn, keys, data):
    if not os.path.exists(fn):
        add_keys_to_xls_file(fn, keys)

    workbook = openpyxl.load_workbook(fn)
    sheet = workbook.active
    add_line_to_xls_sheet(sheet, keys, data)
    workbook.save(fn)


def load_data_file(fn):
    ext = os.path.splitext(fn)[-1].lower()
    if ext=='.xlsx':
        return load_xls_file(fn)
    elif ext=='.csv':
        return load_csv_file(fn)
    else:
        raise '不支持的扩展名'


def load_xls_file(fn, using_pkl_to_cache=False):
    modification_time = 0
    if os.path.exists(fn):
        modification_time = os.path.getmtime(fn)
    if using_pkl_to_cache:
        fn2 = os.path.splitext(fn)[0] + '.pkl'
        if os.path.exists(fn2):
            modification_time2 = os.path.getmtime(fn2)
            if modification_time2>=modification_time:
                with open(fn2, 'rb') as file:
                    data_list = pickle.load(file)
                    return data_list

    # 打开Excel文件
    workbook = openpyxl.load_workbook(fn)
    sheet = workbook.active
    header = [cell.value for cell in sheet[1]]
    data_list = []

    # 遍历除第一行外的每一行数据
    for row in sheet.iter_rows(min_row=2, values_only=True):
        # 创建字典，将每一列的值与对应的列名（键）一一对应
        data_dict = {header[i]: row[i] for i in range(len(header))}
        # 将字典添加到数据列表中
        data_list.append(data_dict)

    if using_pkl_to_cache:
        with open(fn2, 'wb') as file:
            pickle.dump(data_list, file)
    return data_list


def load_csv_file(fn):
#    fn = r"C:\liangz77\python_projects\douyin_data\原始客户数据表-北京1914.csv"

    import chardet

    with open(fn, 'rb') as file:
        detector = chardet.universaldetector.UniversalDetector()
        for line in file:
            detector.feed(line)
            if detector.done:
                break
        detector.close()
        file_encoding = detector.result['encoding']

    with open(fn, mode='r', encoding=file_encoding) as file:
        # 创建CSV读取器
        csv_reader = csv.reader(file)

        infos = []
        keys = None
        for row in csv_reader:
            if keys is None:
                keys = row
                info2 = {}
                for k in keys:
                    info2[k] = ''
                continue
            info = info2.copy()
            for i in range(min(len(row),len(keys))):
                info[keys[i]] = row[i]
            infos.append(info)

#    pkl_fn = os.path.splitext(homepage_fn)[0]+'.pkl'
#    with open(pkl_fn, 'wb') as f:
#        pickle.dump(infos, f)
    return infos


def write_csv_file(fn, infos):
    keys = {}
    for info in infos:
        keys2 = info.keys()
        for k in keys2:
            keys[k] = 0
    if len(keys)==0:
        return
    s = ''
    for k in keys:
        s+=k+','
    f = open(fn, 'w', encoding='utf-8-sig')
    f.write(s[:-1]+'\n')

    print(f'开始写数据，共 {len(infos)} 条')
    for i in range(len(infos)):
        if i%10000==0 and i>0:
            print(f'已写入 {i} 条数据')
        info = infos[i]
        s=''
        for k in keys:
            s = add_val_to_line(s, info, k)
        f.write(s[1:]+'\n')
