from app.ai.model.my_model import MyModel
from langchain.agents import create_agent
"""
摘要智能体，负责提取用户摘要记忆
"""
class SummaryAgent:
    def __init__(self, summary_memory):
        #初始化大模型
        self.model = MyModel.get_local_model()
        #提示词
        self.prompt = self.get_prompt()
        #初始化智能体
        self.agent = self.get_agent()
        #初始化只要记忆存储对象
        self.summary_memory = summary_memory


    def get_prompt(self):
        self.prompt = """
             一: 你是一个对话摘要助手
              你的任务：根据【历史摘要】和【最近聊天记录】生成新的摘要。
              要求：
              1、保留重要信息
              2、去掉闲聊内容
              3、避免重复
              4、控制在200字以内
              5、使用第三人称描述
              6、只返回新的摘要
              7、如果历史摘要和最近聊天记录为没有的时候，则返回0
        """
        return self.prompt

    def get_agent(self):
        self.agent = create_agent(
            model = self.model,
            system_prompt = self.prompt,
            tools = []
        )
        return self.agent

    #更新摘要
    def update(self, session_id, messages):
        #获取历史摘要
        history = self.summary_memory.load_memory(session_id)
        #最新消息
        new_msg = ""
        #提取窗口记忆的信息
        for x in messages:
            new_msg += f"{x["role"]}:{x["content"]}\n"
        # print(f"最新消息：{new_msg}")
        # print(f"历史摘要：{history}")

        #拼接问题
        question = f"历史摘要:{history}\n最近聊天记录：{new_msg}"
        #提问
        rs = self.agent.invoke({"messages":[{"role":"user", "content":question}]})
        #答案
        answer = rs["messages"][-1].content
        if answer != "0":
            #保存摘要记忆
            self.summary_memory.add_memory(session_id,answer)
            #返回答案
        return answer
#测试方法
def test():
    from app.ai.memory.save.summary_memory import SummaryMemory
    from app.ai.memory.save.window_memory import WindowMemory
    s = SummaryMemory()
    w = WindowMemory(1)
    #创建摘要智能体
    agent = SummaryAgent(s)
    #更新摘要
    rs = agent.update(1, w.load())
    print(rs)

if __name__ == "__main__":
    test()
