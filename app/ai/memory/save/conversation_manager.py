from app.ai.memory.save.profile_memory import ProfileMemory
from app.ai.memory.save.window_memory import WindowMemory
from app.ai.memory.save.long_memory import LongMemory
from app.ai.memory.save.summary_memory import SummaryMemory
from app.ai.memory.save.prompt_builder import PromptBuilder
"""
会话记忆管理器
"""
class ConversationManager:

    def __init__(self,session_id:int,user_id:int,question:str):
        self.window_memory = WindowMemory(session_id)
        self.summary_memory = SummaryMemory()
        self.long_memory = LongMemory()
        self.profile_memory =ProfileMemory(session_id)
        self.user_id = user_id
        self.question = question
        self.session_id = session_id

    #添加窗口记忆
    def add_window(self,role,content):
        self.window_memory.add(role,content)
    #添加提示词构造器
    def add_prompt(self):
        builder = PromptBuilder(
            self.window_memory,self.summary_memory,self.long_memory,self.profile_memory,
            self.user_id,self.session_id,self.question
        )
        return builder.builder()
if __name__ == "__main__":
    c = ConversationManager(1,1,"我喜欢什么")
    rs = c.add_prompt()
    print(rs)
    c.add_window("user","你是谁")
    c.add_window("assistant","我是一个助手")