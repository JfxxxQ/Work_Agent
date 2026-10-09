import asyncio
from app.ai.agent.work_agent.excel_agent import ExcelAgent
from app.ai.agent.work_agent.word_agent import WordAgent
from app.ai.agent.router_agent import RouterAgent
import redis
import json
"""
办公主管智能体，负责选择办公智能体
"""
class ManagerAgent:
    def __init__(self):
        #初始excel智能体
        self.excel_agent = ExcelAgent()
        #初始word智能题
        self.word_agent = WordAgent()
        #初始化redis智能体
        self.router_agent = RouterAgent()
        #创建redis链接对象
        self.client = redis.StrictRedis(host="localhost",port=6379,db=0)

    #聊天
    async def chat(self,question,user_id):
        key = f"chat_word:{user_id}"
        # 获取路由智能提返回的结果
        rs = self.router_agent.chat_invoke(question)
        if rs["agent"] == "word_agent":
            async for result in self.word_agent.chat(question):
                yield result
            self.client.set(key, json.dumps(question, ensure_ascii=False), ex=3600)
        else:
            async for result in self.excel_agent.chat(question):
                yield result
            self.client.set(key, json.dumps(question, ensure_ascii=False), ex=3600)

if __name__ =="__main__":
    async def main():
        agent=ManagerAgent()
        user_id="001"
        question = "帮我提取重要内容，文档路径是./test1.docx"
        async for rs in agent.chat(question, user_id):
            print( rs,end="")
    asyncio.run(main())


















