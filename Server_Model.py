# coding: utf-8
import os,time
import numpy as np
from midi.utils import midiwrite
from keras.models import load_model
from configparser import ConfigParser
from CreatePostgresql import Create_PG_SQL
import Upload_Midi2Mp3
from datetime import datetime,timedelta

cfg = ConfigParser()
cfg.read('./config')
mid_total_num = int(cfg['model_server']['mid_total_num'].replace('"',''))
model_path    = cfg['model_server']['model_path'].replace('"','')
music_length_second = int(cfg['model_server']['music_length_second'].replace('"',''))*5
mid_dir       = cfg['model_server']['mid_dir'].replace('"','')

def make_note(mid_path,model):
    temperature = 0.8
    probroll = []
    sampleroll = []
    pressedroll = []
    maxlen = 100
    notes = 88
    x = np.zeros((1, maxlen, notes))
    for i in range(music_length_second):
        predi = model.predict(x, verbose=0)[0]
        predi[predi < 0] = 1E-20  # Avoid negative props
        preds = np.log(predi) / temperature
        exp_preds = np.exp(preds)
        exp_preds = exp_preds * ((1. ** 2 + (predi.sum() / exp_preds.sum()) ** 3) ** 0.5)  # root mean square normalization 

        exp_preds[exp_preds > 1] = 0.99  # Ensure no propability over 1.
        keypressed = np.random.binomial(1, exp_preds)
        sampleroll.append(predi)
        probroll.append(exp_preds)
        pressedroll.append(keypressed)
        x[0, :-1] = x[0, 1:]  # Roll one forward
        x[0, -1] = keypressed  # insert new prediction
    midiwrite(mid_path, pressedroll)
        
def remove_all_file(remove_dir,sub_file_name):
    #remove_dir = remove_dir.replace("/","\\")
    os.system(f"rm {remove_dir}/*.{sub_file_name}")
    
def create_new_url(music_type,ids):
    # 清空
    remove_all_file(mid_dir,"mid")
    print("檔案已清空")
    print("生成對象: ",music_type)
    print("生成ids: ",ids)
    # 篩選(已被使用的音樂連結)
    pg = Create_PG_SQL()
    total_number = int(pg.select_table(f"select total_number from monitor_info where music_type='{music_type}';")[0][0])
    date_list = pg.select_table(f"select create_date from file_info where music_type='{music_type}' and use_status='false' order by create_date ASC;")
    create_date = ''
    if len(date_list)!=0:
        create_date = date_list[0][0]
    #pg.close()
    
    # 生成音樂
    mid_files = []
    for i in range(len(ids)):
        mid_path = f"{mid_dir}/{str(i)}.mid"
        make_note(mid_path,model)
        mid_files.append(mid_path)
    print("mid_files:",mid_files)
    paths = []
    if music_type=="32MBGM":
        paths = Upload_Midi2Mp3.upload_multi_file(mid_files,0)
    elif music_type=="A340":
        paths = Upload_Midi2Mp3.upload_multi_file(mid_files,1)
    elif music_type=="FLUIDR3":
        paths = Upload_Midi2Mp3.upload_multi_file(mid_files,2)
    elif music_type=="PCL":
        paths = Upload_Midi2Mp3.upload_multi_file(mid_files,3)
    else:
        return
    print(paths)

    # 記錄資料
    pg_data = []
    for i in range(len(ids)):
        item2 = [ids[i],
                 paths[i],
                 'false',
                 datetime.now().strftime("%Y/%m/%d"),
                 music_type]
        pg_data.append(item2)

    # 寫入資料庫(postgresql)
    # file_info
    #pg = Create_PG_SQL()
    for item in pg_data:
        pg.upsert_file_info(item)
    # 寫入資料庫(postgresql)
    # monitor_info
    dict_key = {
        "32MBGM":1,
        "A340":2,
        "FLUIDR3":3,
        "PCL":4
    }
    if create_date=='':
        next_day = datetime.now() + timedelta(days=5)
        next_day = next_day.strftime("%Y/%m/%d")
        pg.upsert_monitor_info([dict_key[music_type],0,total_number,next_day,music_type])
    else:
        next_day = create_date + timedelta(days=5)
        next_day = next_day.strftime("%Y/%m/%d")
        pg.upsert_monitor_info([dict_key[music_type],0,total_number,next_day,music_type])
    pg.close()
    
    # 再次清空
    remove_all_file(mid_dir,"mid")
    print("檔案已清空")
    print("生成結束")
    print("="*50)
    
def generator_all_mp3(model):
    # 清空檔案
    # print("清空資料夾...")
    # remove_all_file(mid_dir,"mid")
    # print("="*50)
    
    # 生成音樂
    print("音樂生成中...")
    mid_files = []
    for i in range(mid_total_num*4):
        mid_path = f"{mid_dir}/{str(i)}.mid"
        # make_note(mid_path,model)
        mid_files.append(mid_path)
        print("生成: ",mid_path)
    print("mid_files=",mid_files)
    print("="*50)
    
    # 上傳音樂
    print("音樂上傳中(0)...")
    # v1_paths = Upload_Midi2Mp3.upload_multi_file(mid_files[:mid_total_num],0)
    v1_paths= ['https://tinyurl.com/uv854xg', 'https://tinyurl.com/uu5pwr9', 'https://tinyurl.com/w57bvhn', 'https://tinyurl.com/r2cqtyt', 'https://tinyurl.com/uttgkjf', 'https://tinyurl.com/sc2p9sm', 'https://tinyurl.com/w6sodl2', 'https://tinyurl.com/t7la7kw', 'https://tinyurl.com/t64q8c9', 'https://tinyurl.com/t9y9gcz', 'https://tinyurl.com/tcmhoxm', 'https://tinyurl.com/tkymnvx', 'https://tinyurl.com/ros6pmq', 'https://tinyurl.com/ty2mj3z', 'https://tinyurl.com/tmmb64w', 'https://tinyurl.com/szu7o6d', 'https://tinyurl.com/uqxf8zt', 'https://tinyurl.com/vbls8rw', 'https://tinyurl.com/rjxkdfx','https://tinyurl.com/tmko9uo', 'https://tinyurl.com/qn8xylf', 'https://tinyurl.com/wcyz8vo', 'https://tinyurl.com/ulm7dyw', 'https://tinyurl.com/rn7eczp', 'https://tinyurl.com/tldv9bc', 'https://tinyurl.com/qrk43yd', 'https://tinyurl.com/s46wcpj', 'https://tinyurl.com/sb9dexj', 'https://tinyurl.com/vszpmv3', 'https://tinyurl.com/yx7khq5z', 'https://tinyurl.com/szurq5o', 'https://tinyurl.com/t8p5jmz', 'https://tinyurl.com/wtvktyg', 'https://tinyurl.com/vbo27yz', 'https://tinyurl.com/vv476vg', 'https://tinyurl.com/wbnghvs', 'https://tinyurl.com/sle2bwz', 'https://tinyurl.com/ud84scv', 'https://tinyurl.com/tmt4g9h', 'https://tinyurl.com/wpqj8mq']
    print("音樂上傳中(1)...")
    v2_paths = Upload_Midi2Mp3.upload_multi_file(mid_files[mid_total_num:mid_total_num*2],1)
    print("v2_paths=",v2_paths)
    print("音樂上傳中(2)...")
    v3_paths = Upload_Midi2Mp3.upload_multi_file(mid_files[mid_total_num*2:mid_total_num*3],2)
    print("v3_paths=",v3_paths)
    print("音樂上傳中(3)...")
    v4_paths = Upload_Midi2Mp3.upload_multi_file(mid_files[mid_total_num*3:mid_total_num*4],3)
    print("v4_paths=",v4_paths)
    print("="*50)
    
    # 記錄資料
    print("寫入資料庫...")
    pg_data = []
    for item in v1_paths:
        item2 = [len(pg_data)+1,
                 item,
                 'false',
                 datetime.now().strftime("%Y/%m/%d"),
                 "32MBGM"]
        pg_data.append(item2)
        print(f"32MBGM : {item}")
    for item in v2_paths:
        item2 = [len(pg_data)+1,
                 item,
                 'false',
                 datetime.now().strftime("%Y/%m/%d"),
                 "A340"]
        pg_data.append(item2)
        print(f"A340 : {item}")
    for item in v3_paths:
        item2 = [len(pg_data)+1,
                 item,
                 'false',
                 datetime.now().strftime("%Y/%m/%d"),
                 "FLUIDR3"]
        pg_data.append(item2)
        print(f"FLUIDR3 : {item}")
    for item in v4_paths:
        item2 = [len(pg_data)+1,
                 item,
                 'false',
                 datetime.now().strftime("%Y/%m/%d"),
                 "PCL"]
        pg_data.append(item2)
        print(f"PCL : {item}")
        
    # 寫入資料庫(postgresql)
    # file_info
    pg = Create_PG_SQL()
    for item in pg_data:
        pg.upsert_file_info(item)
        
    # 寫入資料庫(postgresql)
    # monitor_info
    next_day = datetime.now() + timedelta(days=5)
    next_day = next_day.strftime("%Y/%m/%d")
    pg.upsert_monitor_info([1,0,len(v1_paths),next_day,'32MBGM'])
    pg.upsert_monitor_info([2,0,len(v2_paths),next_day,'A340'])
    pg.upsert_monitor_info([3,0,len(v3_paths),next_day,'FLUIDR3'])
    pg.upsert_monitor_info([4,0,len(v4_paths),next_day,'PCL'])
    pg.close()
    print("="*50)
    
    # 再次清空
    print("清空資料夾...")
    remove_all_file(mid_dir,"mid")
    print("="*50)
    
if __name__=="__main__":
    # 載入模型
    model = load_model(model_path)
    # 是否無條件生成
    is_generator_all = False
    if is_generator_all:
        generator_all_mp3(model)
    else:
        # 啟動監聽模式
        while True:
            pg = Create_PG_SQL()
            [v1_use_num,v1_total_num,v1_next_day] = pg.select_table("select use_number,total_number,next_update_date from monitor_info where music_type='32MBGM';")[0]
            [v2_use_num,v2_total_num,v2_next_day] = pg.select_table("select use_number,total_number,next_update_date from monitor_info where music_type='A340';")[0]
            [v3_use_num,v3_total_num,v3_next_day] = pg.select_table("select use_number,total_number,next_update_date from monitor_info where music_type='FLUIDR3';")[0]
            [v4_use_num,v4_total_num,v4_next_day] = pg.select_table("select use_number,total_number,next_update_date from monitor_info where music_type='PCL';")[0]
            #pg.close()
            
            # 日期類型比較
            # datetime.now() = 2020-02-17 22:07:45.866900 ---> <class 'datetime.datetime'>
            # datetime.now().date() = 2020-02-17          ---> <class 'datetime.date'>
            # v1_next_day           = 2020-02-22          ---> <class 'datetime.date'>
            # 相同類型才可以比較大小
            rate = 0.2
            if v1_use_num>int(v1_total_num*rate):
                music_type = '32MBGM'
                ids = pg.select_table(f"select id from file_info where music_type='{music_type}' and use_status='t';")
                create_new_url(music_type,ids)
            elif datetime.now().date()>=v1_next_day:
                music_type = '32MBGM'
                today = datetime.now().strftime('%Y/%m/%d')
                ids = pg.select_table(f"select id from file_info where music_type='{music_type}' and DATEDIFF(day, create_date, '{today}')<1;")
                create_new_url(music_type,ids)
            if v2_use_num>int(v2_total_num*rate):
                music_type = 'A340'
                ids = pg.select_table(f"select id from file_info where music_type='{music_type}' and use_status='t';")
                create_new_url(music_type,ids)
            elif datetime.now().date()>=v2_next_day:
                music_type = 'A340'
                today = datetime.now().strftime('%Y/%m/%d')
                ids = pg.select_table(f"select id from file_info where music_type='{music_type}' and DATEDIFF(day, create_date, '{today}')<1;")
                create_new_url(music_type,ids)
            if v3_use_num>int(v3_total_num*rate):
                music_type = 'FLUIDR3'
                ids = pg.select_table(f"select id from file_info where music_type='{music_type}' and use_status='t';")
                create_new_url(music_type,ids)
            elif datetime.now().date()>=v3_next_day:
                music_type = 'FLUIDR3'
                today = datetime.now().strftime('%Y/%m/%d')
                ids = pg.select_table(f"select id from file_info where music_type='{music_type}' and DATEDIFF(day, create_date, '{today}')<1;")
                create_new_url(music_type,ids)
            if v4_use_num>int(v4_total_num*rate):
                music_type = 'PCL'
                ids = pg.select_table(f"select id from file_info where music_type='{music_type}' and use_status='t';")
                create_new_url(music_type,ids)
            elif datetime.now().date()>=v4_next_day:
                music_type = 'PCL'
                today = datetime.now().strftime('%Y/%m/%d')
                ids = pg.select_table(f"select id from file_info where music_type='{music_type}' and DATEDIFF(day, create_date, '{today}')<1;")
                create_new_url(music_type,ids)
            time.sleep(1)
    
