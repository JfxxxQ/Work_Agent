from app.ai.model.my_model import MyModel
from langchain.agents import create_agent

"""
长期智能体：负责提取用户关键信息，例如 兴趣，偏好，技能，身份
"""
class LongAgent:
    def __init__(self, long_memory):
        # 初始化大模型
        self.model = MyModel.get_local_model()
        # 提示词
        self.prompt = self.get_prompt()
        # 初始化智能体
        self.agent = self.get_agent()
        # 初始化长期记忆存储对象
        self.long_memory = long_memory

    def get_prompt(self):
        self.prompt = """
                一: 你是一个长期记忆提取助手
                二：任务：
                     1 从用户的问题中提取关键信息，例如：
                        兴趣，偏好，技能，
                        身份
                        示例：我是一个人工智能工程师
                        则返回：人工智能工程师
                     2 只返回提取的关键信息，只返回一句话，不需要做任何解释
                     3 如果没有关键信息，则返回0
        """
        return self.prompt

    def get_agent(self):
        self.agent = create_agent(
            model=self.model,
            system_prompt=self.prompt,
            tools=[]
        )
        return self.agent

    # 更新摘要
    def update(self, user_id, question):
        #提问
        rs = self.agent.invoke({"messages": [{"role": "user", "content": question}]})
        # 答案
        answer = rs["messages"][-1].content
        #根据答案判断是否需要保存长期记忆
        if answer !="0":
            self.long_memory.add_memory(user_id,answer)
        return answer

# 测试方法
def test():
    from app.ai.memory.save.long_memory import LongMemory

    s = LongMemory()
    # 创建长期智能体
    agent = LongAgent(s)
    q1="我喜欢编程"
    q2="我是一个人工智能工程师"
    q3="你好，你是谁"
    # 更新摘要
    rs = agent.update(1, q1)
    print(rs)

if __name__ == "__main__":
    test()
