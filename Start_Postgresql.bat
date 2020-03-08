heroku pg:psql --app music-project-a
pause
rem 進入資料庫               : heroku pg:psql --app music-project-a
rem 查看所有資料表           : \dt;
rem 查看指定資料表的詳細資料 : \d table_name;
rem 查看資料庫版本           : SHOW server_version;
rem 離開資料庫               : \q;
rem 刪除資料表               : drop table file_info;
rem 修改資料形態             : alter table file_info alter column mp3_url type text;
rem 更新資料表               : update file_info set use_status='f';
rem update monitor_info set use_number=0;
rem update monitor_info set music_type='game' where id=1;