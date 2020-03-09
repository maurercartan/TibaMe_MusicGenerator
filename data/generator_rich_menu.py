import json,sys
import requests
from linebot.models import RichMenu
from linebot import (
    LineBotApi, WebhookHandler
)
from configparser import ConfigParser

if __name__=="__main__":
    cfg = ConfigParser()
    cfg.read('../config')
    channel_access_token = cfg['line_server']['channel_access_token'].replace('"','')
    rich_menu_json  = f"./{sys.argv[1]}/rich_menu.json"
    rich_menu_id    = f"./{sys.argv[1]}/rich_menu_id"
    rich_menu_img   = f"./{sys.argv[1]}/rich_menu.jpg"   

    # 創建 line_bot_api ,並放入我方的 channel_access_token
    line_bot_api = LineBotApi(channel_access_token)

    # 把(圖文選單設定檔)轉成 json
    menuJson=json.loads(open(rich_menu_json,'r',encoding="utf-8").read())

    # 透過 line_bot_api 把(圖文選單設定檔)上傳給 Line
    lineRichMenuId = line_bot_api.create_rich_menu(rich_menu=RichMenu.new_from_json_dict(menuJson))
    print(lineRichMenuId)
    open(rich_menu_id,'w',encoding="utf-8").write(lineRichMenuId)
    
    # 讀取圖片
    uploadImageFile=open(rich_menu_img,'rb')

    # 將圖片透過 line_bot_api 上傳給 Line
    setImageResponse = line_bot_api.set_rich_menu_image(lineRichMenuId,'image/jpeg',uploadImageFile)