__author__ = 'user'
import os
import psycopg2

class Create_PG_SQL:
    
    def __init__(self):
        # 使用(heroku雲端資料庫)
        self.DATABASE_URL = "postgres://iwldstfnkujljn:d5edada01a0845e3f70f3c2a386cdcfbfcba5fef5030a4492f636c4ecb287118@ec2-35-174-88-65.compute-1.amazonaws.com:5432/dd8olun3m89itp"
        self.conn = psycopg2.connect(self.DATABASE_URL, sslmode='require')
        
    def create_table(self):
        # file_info資料表
        # sql_cmd = '''create table file_info(
            # id serial primary key,
            # mp3_url varchar(100) not null,
            # use_status boolean not null,
            # create_date date not null default current_date,
            # music_type varchar(100) not null
        # );'''
        # monitor_info資料表
        # sql_cmd = '''create table monitor_info(
            # id serial primary key,
            # use_number int not null,
            # total_number int not null,
            # next_update_date date not null,
            # music_type varchar(100) not null
        # );'''
        # user_info資料表
        sql_cmd = '''create table user_info(
            id serial primary key,
            user_id varchar(50) not null,
            type varchar(100) not null,
            number int not null,
            top_10_love text not null
        );'''
    
        cursor = self.conn.cursor()
        cursor.execute(sql_cmd)
        self.conn.commit()
        cursor.close()

    def insert_data(self,myData):
        sql_cmd = "INSERT INTO user_info (select_news,display_name,picture_url,status_message,user_id) \
              VALUES ('"+myData[0]+"','"+myData[1]+"','"+myData[2]+"','"+myData[3]+"','"+myData[4]+"')";
        cursor = self.conn.cursor()
        cursor.execute(sql_cmd)
        self.conn.commit()
        cursor.close()

    def update_data(self,user_id,select_news):
        sql_cmd = "UPDATE user_info set select_news = '"+select_news+"' where user_id='"+user_id+"'";
        cursor = self.conn.cursor()
        cursor.execute(sql_cmd)
        self.conn.commit()
        cursor.close()

    def select_table(self,sql_cmd):
        cursor = self.conn.cursor()
        cursor.execute(sql_cmd)
        data = []
        while True:
            temp = cursor.fetchone()
            if temp:
                data.append(temp)
            else:
                break
        self.conn.commit()
        cursor.close()
        return data

    def update_cmd(self,sql_cmd):
        cursor = self.conn.cursor()
        cursor.execute(sql_cmd)
        self.conn.commit()
        cursor.close()
    
    # 不存在則插入，存在則更新
    # https://www.alibabacloud.com/help/zh/doc-detail/52951.htm
    def upsert_file_info(self,data):
        # data[0] = id         : 流水號
        # data[1] = mp3_url    : 該音樂的(短網址)
        # data[2] = use_status : 該網址是否已被使用
        # data[3] = create_date: 該網址的創建日期
        # data[4] = music_type : 該音樂的類別(game、electronic_keyboard、piano、xylophone)
        cursor = self.conn.cursor()
        sql_cmd = f'''
            insert into file_info values (%s,%s,%s,%s,%s) 
            on conflict (id) do update 
            set mp3_url=%s,use_status=%s,create_date=%s,music_type=%s;
        '''
        print(sql_cmd)
        cursor.execute(sql_cmd,data+[data[1],data[2],data[3],data[4]])
        self.conn.commit()
        cursor.close()
        
    def upsert_monitor_info(self,data):
        # data[0] = id               : 流水號
        # data[1] = use_number       : 該類別已被使用的次數
        # data[2] = total_number     : 該類別的檔案總數
        # data[3] = next_update_date : 該類別的下次更新日期
        # data[4] = music_type       : 音樂的類別(game、electronic_keyboard、piano、xylophone)
        cursor = self.conn.cursor()
        sql_cmd = f'''
            insert into monitor_info values (%s,%s,%s,%s,%s) 
            on conflict (id) do update 
            set use_number=%s,total_number=%s,next_update_date=%s,music_type=%s;
        '''
        cursor.execute(sql_cmd,data+[data[1],data[2],data[3],data[4]])
        self.conn.commit()
        cursor.close()
        
    def upsert_user_info(self,data):
        # data[0] = user_id     : 使用者id
        # data[1] = type        : 類別(game、electronic_keyboard、piano、xylophone、download、user_love)
        # data[2] = num         : 數值(音樂類別的點擊次數,總下載次數,音樂排名)
        # data[3] = top_10_love : 字串(音樂網址)
        cursor = self.conn.cursor()
        sql_cmd = f'''
            insert into user_info(user_id,type,num,top_10_love) 
            values(%s,%s,%s,%s) 
            on conflict (user_id,type) do update 
            set user_id=%s,type=%s,num=user_info.num+1,top_10_love=%s;
        '''
        cursor.execute(sql_cmd,data+[data[0],data[1],data[3]])
        self.conn.commit()
        cursor.close()
        
    def close(self):
        self.conn.close()

if __name__=="__main__":
    pg = Create_PG_SQL()
    # select_news = list(pg.select_table("select * from user_info;"))
    # print(select_news)
    # with open("Select_Database.txt","w",encoding="utf8") as f:
        # for i in range(len(select_news)):
            # f.write(str(select_news[i])+"\n")
    # print(select_news)
    aaa = pg.select_table("select use_number,total_number,next_update_date from monitor_info where music_type='game';")
    print(aaa)
    