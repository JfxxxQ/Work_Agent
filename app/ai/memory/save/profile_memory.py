import redis
from dotenv import load_dotenv
import os
import json
#读取配置我呢见
load_dotenv()
"""
用户画像记忆，记录用户的结构化数据
"""
class ProfileMemory:

    def __init__(self,session_id:int):
        self.client = redis.StrictRedis(host="localhost",port=6379,db=0)
        #设置key
        self.key = f"chat_profile:{session_id}"
    #添加或者更新记忆
    def add(self,hashKey,value):
        self.client.hset(self.key,hashKey,value)
    #查询记忆
    def load(self):
        msg = self.client.hgetall(self.key)
        data=""
        for col,value in msg.items():
            data +=f"{col.decode()}:{self.client.hget(self.key,col).decode()}\n"
        return data
if __name__ =="__main__":
    p = ProfileMemory(1)
    p.add("name","张三")
    p.add("age", 40)
    p.add("job", "程序员")
    rs = p.load()
    print(rs)