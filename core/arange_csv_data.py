from core.stock_io import stock_io, IOSource
from core.tool import *
import os

sio = stock_io(IOSource.Online)

if 0: # 读取csv数据，写成h5数据
    from core.stock_io_csv import *

    for root, dirs, files in os.walk('orig_data/csv数据'):
        for name in files:
            fn = os.path.join(root, name)
            if(fn.find('主力连续')<0):
                continue
            stock = read_stock_csv(fn)
            sio.write_stock(stock)

if 1: # 填写期货代码对应名字
    n = {'cu':'铜','al':'铝','zn':'锌','ru':'天胶','fu':'燃料油','au':'黄金','ag':'白银','rb':'螺纹钢','wr':'线材','pb':'铅',
         'bu':'沥青','hc':'热轧卷板','ni':'镍','sn':'锡','a':'豆一','b':'豆二','m':'豆粕','c':'玉米','y':'豆油','p':'棕榈油',
         'l':'聚乙烯','v':'聚氯乙烯','j':'焦炭','jm':'焦煤','i':'铁矿石','jd':'鸡蛋','fb':'纤维板','bb':'胶合板','pp':'聚丙烯',
         'cs':'玉米淀粉','pm':'普麦','wh':'强麦','cf':'棉花','sr':'白糖','oi':'菜籽油','ta':'PTA','ri':'早籼稻','lr':'晚籼稻',
         'ma':'甲醇','fg':'玻璃','rs':'油菜籽','rm':'菜籽粕','zc':'动力煤','jr':'粳稻','sf':'硅铁','sm':'锰硅','if':'沪深300',
         'ih':'上证50','ic':'中证500','tf':'五债','t':'十债','ap':'苹果','bc':'国际铜','cj':'红枣','cy':'棉纱',
         'eb':'丙乙烯','eg':'乙二醇','er':'籼稻','lh':'生猪','lu':'低硫燃油','me':'甲醇','nr':'20号胶','pf':'短纤','pg':'LPG',
         'pk':'花生','ro':'曾-菜籽油','rr':'粳米','sa':'纯碱','sc':'原油','sp':'纸浆','ss':'不锈钢','tc':'曾-动力煤','ts':'二债',
         'ur':'尿素','ws':'曾-强麦','wt':'硬麦'}
    fn = 'settings/期货.txt'
    fn2 = 'settings/期货2.txt'
    with open(fn, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    with open(fn2, 'w', encoding='utf-8') as f:
        for l in lines:
            if len(l)>0 and l[-1]=='\n':
                l = l[:-1]
            p1 = l.find('次')
            p2 = l.find('主')
            end = p1
            if end<0:
                end = p2
            if end<0:
                f.write(l+'\n')
                continue
            code = l[:end]
            code = code.lower()
            if code in n:
                f.write(l+ ','+n[code]+'\n')
            else:
                print(code)
                f.write(l+ ','+'\n')
