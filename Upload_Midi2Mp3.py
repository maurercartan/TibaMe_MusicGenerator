# coding: utf-8
import json,sys,os
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from bs4 import BeautifulSoup
import urllib
import time
from configparser import ConfigParser
# 關閉警告訊息
import warnings
warnings.filterwarnings('ignore')

cfg = ConfigParser()
cfg.read('./config')
mid_dir = cfg['model_server']['mid_dir'].replace('"','')

def split_json(text):
    index = text.find(":")
    key = text[:index].strip(' ')
    value = text[index + 1:].strip(' ')
    return key,value

def headers_to_dict(headers):
    headers_list = headers.replace(" ","").split("\n")
    result = {}
    for item in headers_list:
        if item!="":
            key,value = split_json(item)
            result[key] = value.strip('"')
    return result
    
# (長網址)轉(短網址)
def long_to_short(long_url):
    r = requests.post(
        "https://tinyurl.com/api-create.php",
        headers={},
        params={},
        data={
            "url":long_url
        })
    return r.text
    
# (短網址)還原(長網址)
def short_to_long(short_url):
    r = requests.post(
        "https://www.ifreesite.com/longurl/url.php",
        headers={},
        params={},
        data={
            "turl":short_url,
            "url_done":"done"
        })
    bs = BeautifulSoup(r.text, "html.parser")
    find_result = bs.find_all("a")
    for item in find_result:
        url = item["href"]
        if "mp3" in url: return url
    return ""
        
# 雲端拋棄式空間: <https://sendit.cloud/>
def upload_cloud(mp3_name,mp3_file):
    # 第1層
    while True:
        try:
            data_flow = urllib.request.urlopen(mp3_file).read()
            break
        except:
            time.sleep(1)
    url = "https://upload.sendit.cloud/cgi-bin/upload.cgi?upload_type=file"
    data = MultipartEncoder(
        fields={
            "sess_id":"", 
            "utype": "anon",
            "file_descr":"",
            "upload": "Upload",
            "link_rcpt":"",
            "link_pass":"",
            "proxyurl":"",
            "keepalive":"1",
            "file_0": (mp3_name,data_flow,"audio/mp3")
        }
    )
    r = requests.post(
        url,
        headers={'Content-Type': data.content_type},
        params={},
        data=data,
        verify=False)
    file_code = json.loads(r.text)[0]["file_code"]
    url2 = "https://sendit.cloud/"+file_code
    
    # 第2層
    r2 = requests.get(
        url2,
        headers={"User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36"},
        params={},
        data={})
    bs = BeautifulSoup(r2.text, "html.parser")
    find_result = bs.find_all("div")
    url3 = ""
    for item in find_result:
        if "data-source" in str(item):
            try:
                if "mp3" in item["data-source"]: url3 = item["data-source"]
            except:pass
    return url3
    
# Midi to Mp3 <https://solmire.com/midi-to-mp3>
# midi轉mp3
def upload_midi_to_mp3(mid_name,mid_file,sf_code_num):
    #sf_code = ["SGM2","PC51","PCL","GUS","UNISON","CHORIUM","TITANIC","MAGICSF2","32MBGM",
    #          "A340","CADENZA","FLUIDR3","GENUS","MERLIN","XIOAD","SAPHYR","REALITY","JURGEN","FF7",
    #          "ARACHNO","TIMBERS","SUPERMARIO64","COMPIFONT","OMEGA"]
    sf_code = ["32MBGM","A340","FLUIDR3","PCL"]
    url = "https://solmire.com/upload.php"
    data = MultipartEncoder(
        fields={
            "tk":"DuFAyvhjM551BxhIt8FO", 
            "midi": (mid_name,open(mid_file, 'rb').read(),"audio/mid"),
            "instruments":sf_code[sf_code_num],
            "tempo":"100",
            "key": "0",
            "channels":"2",
            "bitrate":"128",
            "hq":"0",
            "genre":"40",
            "trim":"1",
            "share":"1",
            "submit":"Upload and Convert!"
        }
    )

    r = requests.post(
        url,
        headers={'Content-Type': data.content_type},
        params={},
        data=data,
        verify=False)
    bs = BeautifulSoup(r.text, "html.parser",from_encoding="utf8")
    find_result = bs.find_all("a")
    result = ""
    for item in find_result:
        if "Your Converted Midi File" in str(item):
            try:
                result = item["href"].split('?')[0]
            except:pass
    return result
        
def upload_multi_file(mid_files,sf_code_num):
    result = []
    upload_url = []
    for file_path in mid_files:
        file_name = os.path.basename(file_path)
        # (midi)轉(mp3)
        url = upload_midi_to_mp3(file_name,file_path,sf_code_num)
        print(url)
        upload_url.append(url)
    print(upload_url)
    time.sleep(10) # 因為(上傳)與(轉換)等待
    count = 0
    for url in upload_url:
        print("id = ",mid_files[count])
        print("轉換後連結 = ",url)
        # 上傳到(雲端拋棄空間)
        url2 = upload_cloud(url.rsplit('/', 1)[-1],url)
        print("上傳雲端連結 = ",url2)
        # (長網址)轉(短網址)
        url3 = long_to_short(url2)
        print("短網址 = ",url3)
        result.append(url3)
        count += 1
    return result
        
if __name__ == "__main__":
    mid_name = "1.mid"
    mid_file = "./pre_generator_music/1.mid"
    sf_code_num = 0
    upload_multi_file([mid_file],sf_code_num)
    # mp3_file = "https://solmire.com/uploads/1582095767_kzXWFnYAqw6cibUSv3o9.mp3"
    # name = mp3_file.rsplit('/', 1)[-1]
    # data_flow = urllib.request.urlopen(mp3_file).read()
    # print(data_flow)
    # print(name)
   