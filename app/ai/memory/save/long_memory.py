import chromadb
import os
from dotenv import load_dotenv
import time

#读取配置文件
load_dotenv()
"""
长期记忆，记忆存储用户的偏好信息
"""
class LongMemory:
    def __init__(self):
        #读取向量数据库
        self.client = chromadb.PersistentClient(path=os.getenv("CHROM_DB_URL"))
        #获取集合
        self.collection = self.client.get_or_create_collection(os.getenv("CHROM_DB_NAME"))

    def add_memory(self, user_id, content:str):
        #设置向量数据库id保持唯一，用户id只有1个
        id = f"{user_id}{time.strftime('%Y%m%d%H%M%S', time.localtime())}"
        self.collection.add(
            ids = [id],
            documents = [content],
            metadatas = [
                {"user_id":user_id}
            ]
        )
    #获取记忆
    def load_memory(self, user_id, question):
        rs = self.collection.query(
            query_texts = [question],
            n_results = 3,
            where = {
                "user_id":user_id
            }
        )
        return rs["documents"][0]

#测试方法
def test():
    l = LongMemory()
    l.add_memory(1,"我正在学习langchain")
    l.add_memory(1, "我正在学习python")
    l.add_memory(1, "我喜欢看书")
    l.add_memory(1, "我正在学习向量数据库")

if __name__ =="__main__":
   test()
   l = LongMemory()
   rs = l.load_memory(1,"我喜欢什么")
   print(rs)
   #test01()