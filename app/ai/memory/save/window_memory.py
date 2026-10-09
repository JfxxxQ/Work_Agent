import redis
from dotenv import load_dotenv
import os
import json
#读取配置文件
load_dotenv()
"""
窗口记忆，记录最近的4轮的窗口记忆
"""

class WindowMemory:
    def __init__(self, session_id : int):
        self.client = redis.StrictRedis(host = "localhost", port = 6379, db = 0)
        #设置key
        self.key = f"chat_window:{session_id}"
        #获取轮次
        self.window_size = int(os.getenv("WINDOW_SIZE"))
        #获取过期时间
        self.window_time = int(os.getenv("WINDOW_TIME"))

    #添加记忆
    def add(self, role : str, content : str):
        #构建一个字典
        msg = {"role" : role, "content" : content}
        #序列化
        msg_json = json.dumps(msg, ensure_ascii=False)
        #列表完成数据追加
        self.client.rpush(self.key, msg_json)
        #设置窗口的限制条数，剩下的删除
        self.client.ltrim(self.key, -self.window_size, -1)
        #设置过期时间
        self.client.expire(self.key, self.window_time)

    #查询记忆
    def load(self):
        msg = self.client.lrange(self.key, 0, -1)
        return [json.loads(x) for x in msg]

#测试函数
def test():
    w = WindowMemory(1)
    # 模拟人类消息添加
    w.add("user", "你好")
    # 模拟AI回复消息
    w.add("ai", "你好，我是AI助手")
    # 模拟人类消息添加
    w.add("user", "你好1")
    # 模拟AI回复消息
    w.add("ai", "你好1，我是AI助手1")
    # 模拟人类消息添加
    w.add("user", "你好2")
    # 模拟AI回复消息
    w.add("ai", "你好2，我是AI助手2")
    w.add("user", "你好3")
    # 模拟AI回复消息
    w.add("ai", "你好3，我是AI助手2")
    # 查询记忆
    rs = w.load()
    print(rs)


if __name__ == "__main__":
    test()