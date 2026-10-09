from app.ai.memory.retrieval.long_agent import LongAgent
from app.ai.memory.retrieval.profile_agent  import ProfileAgent
from app.ai.memory.retrieval.summary_agent import SummaryAgent
from dotenv import load_dotenv
import os

#读取配置文件
load_dotenv()
"""
记忆管理
"""
class MemoryManager:
    def __init__(self,conversion):
        # 创建长期记忆智能体
        self.long_agent = LongAgent(conversion.long_memory)
        # 创建摘要记忆智能体
        self.summary_agent = SummaryAgent(conversion.summary_memory)
        # 创建画像记忆智能体
        self.profile_agent = ProfileAgent(conversion.profile_memory)
        #创建窗口记忆
        self.window = conversion.window_memory
        #用户id
        self.user_id = conversion.user_id
        #会话id
        self.session_id =conversion.session_id

     #更新所有记忆
    def update(self,question):
        #更新画像记忆
        self.profile_agent.update(question)
        #更新长期记忆
        self.long_agent.update(self.user_id, question)
        #更新摘要记忆
        self.summary_agent.update(self.session_id,self.window.load())


