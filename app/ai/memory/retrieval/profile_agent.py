from app.ai.model.my_model import MyModel
from langchain.agents import create_agent
import json

"""
用户画像记忆提取智能体：负责提取用户结构化数据，例如 姓名，年龄，性别，公司，职位
"""


class ProfileAgent:
    def __init__(self, profile_memory):
        # 初始化大模型
        self.model = MyModel.get_local_model()
        # 提示词
        self.prompt = self.get_prompt()
        # 初始化智能体
        self.agent = self.get_agent()
        # 初始化用户画像记忆存储对象
        self.profile_memory = profile_memory

    def get_prompt(self):
        self.prompt = """
              一: 你是一个用户画像记忆提取助手
              二：任务
                     1 从用户问题提取结构化数据，例如 姓名，年龄，性别，公司，职位
                     2 提取结构化数据是以下数据
                        name:姓名
                        age:年龄
                        sex:性别
                        company:公司
                        job:职位
                     3 如果没有结构化数据，则返回{}
                     4 如果用结构化数据，则返回以下格式
                       示例：
                         用户：我叫张三 返回 {"name":"张三"}
                         用户：我叫张三，今年24岁 返回 {"name":"张三","age":"24"}
                         用户：我叫张三 今年24岁，在华为做程序员 {"name":"张三","age":"24","company":"华为","job":"程序员"}
                         用户：我叫张三 ，我是男的  {"name":"张三","sex":"男"}
                
              三：输出  
                       - 只输出 JSON
                      - 不允许输出 Markdown
                      - 不允许输出 ```json
                      - 不允许输出解释说明
                      - 不允许输出多个 JSON
                      - 不允许输出任何额外文字
                      - JSON 必须能够被 `json.loads()` 正确解析

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
    def update(self, question):
        # 提问
        rs = self.agent.invoke({"messages": [{"role": "user", "content": question}]})
        # 答案
        answer = rs["messages"][-1].content
        data = json.loads(answer)
        # 返回答案:  name:张胜男
        if not data:
            return {}
        for key, value in data.items():
            self.profile_memory.add(key, value)
        return data


# 测试方法
def test():
    from app.ai.memory.save.profile_memory import ProfileMemory

    s = ProfileMemory(1)
    # 创建长期智能体
    agent = ProfileAgent(s)
    q1 = "我叫王五"
    q2 = "我的公司是华清远见"
    q3 = "你好，你是谁"
    # 更新摘要
    rs = agent.update(q2)
    print(rs)


if __name__ == "__main__":
    test()
