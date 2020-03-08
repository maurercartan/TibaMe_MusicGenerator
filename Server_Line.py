# coding: utf-8
'''

midi to wav:
    E:\software\fluidsynth\fluidsynth-x64\bin\fluidsynth
    E:\software\MIDIRenderer\midirenderer
    E:\software\SOX\sox-14-4-2\sox
    
wav to mp3:
    E:\software\FFmpeg\bin\ffmpeg
    
midi to mp3:
    E:\software\TiMidity\timidity

'''

# 引用Web Server套件
from flask import Flask, request, abort

# 從linebot 套件包裡引用 LineBotApi 與 WebhookHandler 類別
from linebot import (
    LineBotApi, WebhookHandler
)

# 引用無效簽章錯誤
from linebot.exceptions import (
    InvalidSignatureError
)

# 引用套件
from linebot.models import (
    ImagemapSendMessage,
    TextSendMessage,
    ImageSendMessage,
    LocationSendMessage,
    VideoSendMessage,
    AudioSendMessage,
    TextMessage,
    FollowEvent,
    MessageEvent,
    PostbackEvent,
    QuickReply, 
    QuickReplyButton,
    PostbackAction,
    FlexSendMessage,
    BubbleContainer,
    FlexSendMessage,
    CarouselContainer,
    MessageAction
)
from linebot.models.template import (
    ButtonsTemplate,CarouselTemplate,ConfirmTemplate,ImageCarouselTemplate
)
from linebot.models.template import *

import os
from configparser import ConfigParser
import Upload_Midi2Mp3
from CreatePostgresql import Create_PG_SQL

# 載入基礎設定檔
cfg = ConfigParser()
cfg.read('./config')
channel_access_token   = cfg['line_server']['channel_access_token'].replace('"','')
secret_key             = cfg['line_server']['secret_key'].replace('"','')
rich_menu_id_title     = cfg['line_server']['rich_menu_id_title'].replace('"','')
rich_menu_id_generator = cfg['line_server']['rich_menu_id_generator'].replace('"','')
rich_menu_id_null      = cfg['line_server']['rich_menu_id_null'].replace('"','')
mid_total_num          = int(cfg['model_server']['mid_total_num'].replace('"',''))
music_length_second    = int(cfg['model_server']['music_length_second'].replace('"',''))

# 設定Server啟用細節
# static_url_path,static_folder --> 共享目錄
app = Flask(__name__,static_url_path = "/output_music_to_linebot" , static_folder = "/output_music_to_linebot/")

# 生成實體物件
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(secret_key)

# 啟動server對外接口，使Line能丟消息進來
@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 關注事件處理
@handler.add(FollowEvent)
def process_follow_event(event):
    # 綁定(圖文選單)
    linkRichMenuId = open(rich_menu_id_title, 'r').read()
    line_bot_api.link_rich_menu_to_user(event.source.user_id,linkRichMenuId)

def return_file_exist():
    for i in range(mid_total_num):
        path_v1  = f'./pre_generator_music/mp3_v1/{i}.mp3'
        path_v2  = f'./pre_generator_music/mp3_v2/{i}.mp3'
        path_v3  = f'./pre_generator_music/mp3_v3/{i}.mp3'
        path_v4  = f'./pre_generator_music/mp3_v4/{i}.mp3'
        del_path = f'./pre_generator_music/mid/{i}.mid'
        print(del_path)
        if os.path.isfile(del_path):
            return [path_v1,path_v2,path_v3,path_v4], del_path
    return [],""
    
    
# 文字消息處理
@handler.add(MessageEvent,message=TextMessage)
def process_text_message(event):
    # 讀取本地檔案，並轉譯成消息
    result_message_array =[]
    if event.message.text=="#音樂生成":
        # 綁定(圖文選單)
        linkRichMenuId = open(rich_menu_id_generator, 'r').read()
        line_bot_api.link_rich_menu_to_user(event.source.user_id,linkRichMenuId)
    elif event.message.text=="#風格轉換":
        # 綁定(圖文選單)
        linkRichMenuId = open(rich_menu_id_null, 'r').read()
        line_bot_api.link_rich_menu_to_user(event.source.user_id,linkRichMenuId)
    elif event.message.text=="#使用者資訊":
        # 綁定(圖文選單)
        linkRichMenuId = open(rich_menu_id_null, 'r').read()
        line_bot_api.link_rich_menu_to_user(event.source.user_id,linkRichMenuId)
    elif event.message.text=="#UNISON":
        music_type='UNISON'
        pg = Create_PG_SQL()
        [id,mp3_url] = pg.select_table("select id,mp3_url from file_info where use_status='f' and music_type='%s';"%music_type)[0]
        long_url = Upload_Midi2Mp3.short_to_long(mp3_url) # (短網址)還原(長網址)
        try:
            #語音訊息
            audio_message = AudioSendMessage(original_content_url=long_url,duration=music_length_second*1000)
            # 發送
            line_bot_api.reply_message(event.reply_token,audio_message)
        except:
            pass
        pg.update_cmd("update file_info set use_status='t' where id=%s"%id)
        pg.update_cmd("update monitor_info set use_number=use_number+1 where music_type='%s'"%music_type)
        pg.upsert_user_info([event.source.user_id,music_type,1,""])
        pg.close()
    elif event.message.text=="#SUPERMARIO64":
        music_type='SUPERMARIO64'
        pg = Create_PG_SQL()
        [id,mp3_url] = pg.select_table("select id,mp3_url from file_info where use_status='f' and music_type='%s';"%music_type)[0]
        long_url = Upload_Midi2Mp3.short_to_long(mp3_url) # (短網址)還原(長網址)
        try:
            #語音訊息
            audio_message = AudioSendMessage(original_content_url=long_url,duration=music_length_second*1000)
            # 發送
            line_bot_api.reply_message(event.reply_token,audio_message)
        except:
            pass
        pg.update_cmd("update file_info set use_status='t' where id=%s"%id)
        pg.update_cmd("update monitor_info set use_number=use_number+1 where music_type='%s'"%music_type)
        pg.upsert_user_info([event.source.user_id,music_type,1,""])
        pg.close()
    elif event.message.text=="#REALITY":
        music_type='REALITY'
        pg = Create_PG_SQL()
        [id,mp3_url] = pg.select_table("select id,mp3_url from file_info where use_status='f' and music_type='%s';"%music_type)[0]
        long_url = Upload_Midi2Mp3.short_to_long(mp3_url) # (短網址)還原(長網址)
        try:
            #語音訊息
            audio_message = AudioSendMessage(original_content_url=long_url,duration=music_length_second*1000)
            # 發送
            line_bot_api.reply_message(event.reply_token,audio_message)
        except:
            pass
        pg.update_cmd("update file_info set use_status='t' where id=%s"%id)
        pg.update_cmd("update monitor_info set use_number=use_number+1 where music_type='%s'"%music_type)
        pg.upsert_user_info([event.source.user_id,music_type,1,""])
        pg.close()
    elif event.message.text=="#FF7":
        music_type='FF7'
        pg = Create_PG_SQL()
        [id,mp3_url] = pg.select_table("select id,mp3_url from file_info where use_status='f' and music_type='%s';"%music_type)[0]
        long_url = Upload_Midi2Mp3.short_to_long(mp3_url) # (短網址)還原(長網址)
        try:
            #語音訊息
            audio_message = AudioSendMessage(original_content_url=long_url,duration=music_length_second*1000)
            # 發送
            line_bot_api.reply_message(event.reply_token,audio_message)
        except:
            pass
        pg.update_cmd("update file_info set use_status='t' where id=%s"%id)
        pg.update_cmd("update monitor_info set use_number=use_number+1 where music_type='%s'"%music_type)
        pg.upsert_user_info([event.source.user_id,music_type,1,""])
        pg.close()
    elif event.message.text=="#上一頁":
        # 綁定(圖文選單)
        linkRichMenuId = open(rich_menu_id_title, 'r').read()
        line_bot_api.link_rich_menu_to_user(event.source.user_id,linkRichMenuId)
    elif event.message.text=="#qrcode":
        # 傳送QR-code圖片
        img_url = "https://qr-official.line.me/sid/L/673vaqvk.png"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=img_url)
        )
    
if __name__ == "__main__":
    # 本地執行
    #app.run(host='0.0.0.0')
    
    # 雲端執行
    app.run(host='0.0.0.0',port=os.environ['PORT'])