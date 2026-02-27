import sys
import os
import subprocess
from db import init_db_pool
from flask import Flask, request
from config import BaseConfig
import logging
from logging_config import setup_logging

from psycopg2.extras import RealDictCursor
from db import get_db

"""创建应用，支持测试配置"""
app = Flask(__name__)


app.config.from_object(BaseConfig)

# 初始化数据库
# ⭐ 只初始化一次
init_db_pool(app.config)

file_path = './database/data/lesson_05/words_01.json'
book = 2
lesson = 5

import json

with get_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                try:
                    sql = """
                            insert into words(
                                book,
                                lesson,
                                french, 
                                chinese, 
                                part_of_speech, 
                                part_of_speech_full_chinese)values(
                                    %d,
                                    %d,
                                    '%s',
                                    '%s',
                                    '%s',
                                    '%s'
                                )
                    """
                    cnt = 0
                    for d in data:
                        # print(d)
                        _sql = sql %(book,
                                     lesson,
                                     d['french'].replace("'","''"),
                                     d['chinese'].replace("'","''"),
                                     d['part_of_speech'].replace("'","''"),
                                     d['part_of_speech_full_chinese'].replace("'","''"))
                        # print(_sql)
                        cur.execute(_sql)
                        cnt = cnt+1
                        print(cnt)

                    conn.commit()
                except Exception as e:
                    print(f'出现错误了,{str(e)}')
                    conn.rollback()