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

import os,json
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
rich_menu_id_style      = cfg['line_server']['rich_menu_id_style'].replace('"','')
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

def detect_json_array_to_new_message_array(fileName):
    
    #開啟檔案，轉成json
    with open(fileName) as f:
        jsonArray = json.load(f)
    
    # 解析json
    returnArray = []
    for jsonObject in jsonArray:

        # 讀取其用來判斷的元件
        message_type = jsonObject.get('type')
        
        # 轉換
        if message_type == 'text':
            returnArray.append(TextSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'imagemap':
            returnArray.append(ImagemapSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'template':
            returnArray.append(TemplateSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'image':
            returnArray.append(ImageSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'sticker':
            returnArray.append(StickerSendMessage.new_from_json_dict(jsonObject))  
        elif message_type == 'audio':
            returnArray.append(AudioSendMessage.new_from_json_dict(jsonObject))  
        elif message_type == 'location':
            returnArray.append(LocationSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'flex':
            returnArray.append(FlexSendMessage.new_from_json_dict(jsonObject))  
        elif message_type == 'video':
            returnArray.append(VideoSendMessage.new_from_json_dict(jsonObject))    


    # 回傳
    return returnArray


# 關注事件處理
@handler.add(FollowEvent)
def process_follow_event(event):
    # 綁定(圖文選單)
    linkRichMenuId = open(rich_menu_id_title, 'r').read()
    line_bot_api.link_rich_menu_to_user(event.source.user_id,linkRichMenuId)
    
    # 讀取並轉換
    result_message_array =[]
    replyJsonPath = "data/join/001/reply.json"
    replyJsonPath2 = "data/join/002/reply.json"
    result_message_array += detect_json_array_to_new_message_array(replyJsonPath)
    result_message_array += detect_json_array_to_new_message_array(replyJsonPath2)

    # 消息發送
    line_bot_api.reply_message(
        event.reply_token,
        result_message_array
    )
    
    
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
        linkRichMenuId = open(rich_menu_id_style, 'r').read()
        line_bot_api.link_rich_menu_to_user(event.source.user_id,linkRichMenuId)
    elif event.message.text=="#使用者資訊":
        # 綁定(圖文選單)
        linkRichMenuId = open(rich_menu_id_style, 'r').read()
        line_bot_api.link_rich_menu_to_user(event.source.user_id,linkRichMenuId)
    elif event.message.text=="#32MBGM":
        music_type='32MBGM'
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
    elif event.message.text=="#A340":
        music_type='A340'
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
    elif event.message.text=="#FLUIDR3":
        music_type='FLUIDR3'
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
    elif event.message.text=="#PCL":
        music_type='PCL'
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
    
@handler.add(PostbackEvent)
def process_postback_event(event):
    query_string_dict = parse_qs(event.postback.data)

    if 'text' in query_string_dict:
        text = query_string_dict.get('text')[0]
        if text=="製作音樂":
            pass
        elif text=="播放紀錄":
            pass
        elif text=="關於我們":
            pass
        elif text=="R3音源":
            pass
        elif text=="A340音源":
            pass
        elif text=="通用音樂風格":
            pass
        elif text=="寫實風格":
            pass
        elif text=="輕快風格":
            pass
        elif text=="回主選單":
            pass
        elif text=="其他靈感":
            pass
        elif text=="鄉村音樂":
            pass
        elif text=="民謠音樂":
            pass
        elif text=="爵士音樂":
            pass
        elif text=="搖滾音樂":
            pass
        elif text=="藍調音樂":
            pass
        elif text=="古典音樂":
            pass
        elif text=="disco":
            pass
        elif text=="福音音樂":
            pass
if __name__ == "__main__":
    # 本地執行
    #app.run(host='0.0.0.0')
    
    # 雲端執行
    app.run(host='0.0.0.0',port=os.environ['PORT'])