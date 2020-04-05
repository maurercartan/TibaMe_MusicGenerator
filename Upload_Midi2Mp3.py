# coding: utf-8
import json,sys,os
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from bs4 import BeautifulSoup
import urllib
import time
from configparser import ConfigParser
import random,string
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
    url = "https://wwww.sendit.cloud/cgi-bin/upload.cgi?upload_type=file"
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
    print(r.text)
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
    
def dict_to_string(cookies):
    return "; ".join([str(x)+"="+str(y) for x,y in cookies.items()])
    
# 雲端拋棄式空間: <https://bitsend.jp/>
# 參考資料: https://www.jianshu.com/p/902452189ca9
def upload_cloud_v2(mp3_name,mp3_file):
    with requests.Session() as s:
        
        # 第1層
        r = s.get(
            "https://bitsend.jp/",
            headers={
                "User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36",
                "Cookie":dict_to_string(s.cookies.get_dict())
            },
            params={},
            data={})
        bs = BeautifulSoup(r.text, "html.parser")
        find_result = bs.find_all("input")
        u_key = ""
        for item in find_result:
            if "u_key" in str(item):
                try:
                    u_key = item["value"]
                    break
                except:pass
        print(f"u_key = {u_key}")
        # 第2層
        while True:
            try:
                data_flow = urllib.request.urlopen(mp3_file).read()
                break
            except:
                time.sleep(1)
        data = MultipartEncoder(
            fields={
                "u_key":u_key,
                "files[]": (mp3_name,data_flow,"audio/mp3")
            },
            boundary='----WebKitFormBoundary'+''.join(random.sample(string.ascii_letters+string.digits,16))
        )
        r2 = s.post(
            "https://bitsend.jp/jqu/",
            headers={
                'Accept':'application/json, text/javascript, */*; q=0.01',
                'Accept-Encoding':'gzip, deflate, br',
                'Accept-Language':'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'Connection':'keep-alive',
                'Content-Length':'193592',
                'Content-Type': data.content_type,
                'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
                'Host':'bitsend.jp',
                'Origin':'https://bitsend.jp',
                'Referer':'https://bitsend.jp/',
                'Sec-Fetch-Dest':'empty',
                'Sec-Fetch-Mode':'cors',
                'Sec-Fetch-Site':'same-origin',
                'X-Requested-With':'XMLHttpRequest',
                "Cookie":dict_to_string(s.cookies.get_dict())
            },
            params={},
            data=data,
            timeout=10)
        file_code = json.loads(r2.text)["files"][0]["fileKey"]
        url2 = f"https://bitsend.jp/download/{file_code}.html"
        print(f"url2 = {url2}")
        # 第3層
        r3 = s.get(
            url2,
            headers={"User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36"},
            params={},
            data={})
        
        bs = BeautifulSoup(r3.text, "html.parser")
        find_result2 = bs.find_all("a")
        url3 = ""
        for item in find_result2:
            if "btn-download" in str(item):
                try:
                    url3 = item["href"]
                    break
                except:pass
        url4 = "https://bitsend.jp"+url3
        print(f"url4 = {url4}")
    return url4
    
# Midi to Mp3 <https://solmire.com/midi-to-mp3>
# midi轉mp3
def upload_midi_to_mp3(mid_name,mid_file,sf_code_num):
    #sf_code = ["SGM2","PC51","PCL","GUS","UNISON","CHORIUM","TITANIC","MAGICSF2","32MBGM",
    #          "A340","CADENZA","FLUIDR3","GENUS","MERLIN","XIOAD","SAPHYR","REALITY","JURGEN","FF7",
    #          "ARACHNO","TIMBERS","SUPERMARIO64","COMPIFONT","OMEGA"]
    sf_code = ["32MBGM","A340","FLUIDR3","PCL","REALITY"]
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
        #url2 = upload_cloud_v2(url.rsplit('/', 1)[-1],url)
        print("上傳雲端連結 = ",url2)
        # (長網址)轉(短網址)
        url3 = long_to_short(url2)
        print("短網址 = ",url3)
        result.append(url3)
        count += 1
    return result
        
if __name__ == "__main__":
    # mid_name = "1.mid"
    # mid_file = "./pre_generator_music/1.mid"
    # sf_code_num = 0
    # upload_multi_file([mid_file],sf_code_num)
    # mp3_file = "https://solmire.com/uploads/1582095767_kzXWFnYAqw6cibUSv3o9.mp3"
    # name = mp3_file.rsplit('/', 1)[-1]
    # data_flow = urllib.request.urlopen(mp3_file).read()
    # print(data_flow)
    # print(name)
    url = "https://solmire.com/uploads/1585577559_wByUnjpHSFEeLq4YAwcQ.mp3"
    url2 = upload_cloud_v2(url.rsplit('/', 1)[-1],url)
    print(url2)
   