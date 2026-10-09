from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from app.ai.tool.mysql_tool import mysql_tool
from app.ai.model.my_model import MyModel
from langgraph.checkpoint.memory import InMemorySaver
from app.ai.memory.memory_manager import MemoryManager
from app.ai.memory.save.conversation_manager import ConversationManager

"""
聊天智能体
"""


class ChatAgent:

    def __init__(self):
        self.model_memory = MyModel.get_local_model()
        self.model = MyModel.get_line_model()
        self.prompt = self.get_prompt()
        self.tool = self.get_tool()
        self.agent = self.get_agent()

    # 加载提示词
    def get_prompt(self):
        self.prompt = """
           一 角色
            你是通用聊天助手，负责日常问候、闲聊、知识答疑、业务咨询，同时可以调用MySQL数据库完成数据查询。
            
           二 能力范围
            1. 日常交互：支持打招呼、问候、情绪安抚、普通闲聊，正常进行多轮对话。
            2. 知识答疑：解答常识、概念解释、方案咨询等各类普通问题。
            3. 数据库查询能力：当用户问题需要查询业务库数据时，调用MySQL工具获取数据，再整理成自然语言回复用户。
            4. 业务记忆：当用户提出文档摘要/重要内容、表格填充的内容这类要求的时候，请查询数据库提取对应的chat_word 或 chat_excel记忆，并返回给用户
            4. 边界：不处理Word/Excel文档解析、文档摘要、表格填充类任务；这类任务属于办公智能体能力，如果用户提出文档相关需要使用工具的需求，请提示用户上传文件触发办公智能体。
            
           三 重要规则
            1. 判断是否需要访问MySQL
            - 如果用户提问是**业务数据查询、查记录、查统计、查列表**等需要数据库的内容，不要自己编造数据，调用MySQL工具执行查询。
            - 如果是普通闲聊、常识问答，不需要调用数据库，直接回答。
            - 如果是用户提出之前干过什么可以调用数据库查询历史提问记录
            
            2. 数据库调用约束
            - 只做查询SELECT，禁止生成DELETE、UPDATE、ALTER、DROP、INSERT等修改、删除表/数据的SQL语句。
            - 生成SQL尽量严谨，字段、表名尽量贴合业务，条件尽量合理；查询结果为空，如实告知用户“未查询到相关数据”，不要虚构结果。
            - 查询返回原始数据后，不要直接输出原始JSON/原始表格，把数据整理成通顺易懂的自然语言展示给用户。
            
            3. 拒绝越权操作
            用户要求修改、删除数据库数据，直接拒绝，明确告知不支持数据修改操作。
            
            4. 任务分流规则
            当用户提到word、excel、文档摘要、表格填充、提取文档数据填表，提醒用户：该功能属于办公智能体，请上传对应的Word、Excel文件进行处理，本聊天智能体不处理文档解析任务。
            
            5. 回答风格
            语气自然友好，简洁易懂；复杂查询结果可以适当分段展示；不确定的内容不要编造。
            
           四 输出格式
            - 普通问答：直接输出自然语言回答。
            - 需要查询数据库：触发工具调用，不要自己脑补数据。
            - 查询得到数据：对数据做整理、总结，再给到用户。
            - 查无数据：如实告知用户未查到，可引导用户确认查询条件。
 
           五 数据导出流程步骤如下
              你必须严格按照以下步骤来执行
                步骤一：理解用户需求，调用mysql_tool工具查询数据
                步骤二：查询出数据，以表格显示数据
                步骤三：返回表格内容
           六 规则
              1 你必须严格按照各个流程步骤执行
              2 返回的数据必须是markdown格式
           七 输出
              1 必须按照各个流程的数据格式输出


         """
        return self.prompt

    # 加载工具
    def get_tool(self):
        self.tool = [mysql_tool]
        return self.tool

    # 加载智能体
    def get_agent(self):

        self.agent = create_agent(
            model=self.model,
            tools=self.tool,
            system_prompt=self.prompt,
            checkpointer=InMemorySaver(),  # 添加记忆功能，检查点
            middleware=[SummarizationMiddleware(
                model=self.model_memory,
                trigger=("tokens", 150),  # 超过150token触发摘要，替换旧max_tokens_before_summary
                max_tokens_after_summary=150,
                min_tokens=150,
                keep=("messages", 2)  # 保留最近2条原始消息，替换旧messages_to_keep
            )]
        )
        return self.agent

    # 同步聊天
    def chat_invoke(self, question):
        try:
            msg = {"messages": [{"role": "user", "content": question}]}
            rs = self.agent.invoke(msg)
            return rs["messages"][-1].content
        except Exception as e:
            print(f"同步聊天出现异常:{e}")
            return "同步聊天出现异常"

    # 异步聊天
    async def chat(self, question, user_id):
        try:
            # 添加四层记忆
            c = ConversationManager(user_id, user_id, question)
            m = MemoryManager(c)
            # 添加窗口记忆用户问题
            c.add_window("user", question)
            # 构建记忆的提示词
            memory_prompt = c.add_prompt()
            # 构建一个系统角色消息
            sys_msg = {"role": "system", "content": memory_prompt}
            msg = {"messages": [{"role": "user", "content": question}, sys_msg]}

            config = {"configurable": {"thread_id": user_id}}
            rs = self.agent.astream_events(msg, config, version="v2")
            # 定义回复ai消息变量
            ai_msg = ""
            async for event in rs:
                # 获取事件类型
                event_type = event["event"]
                if event_type == "on_tool_start":
                    yield f"\n 开始执行工具:{event["name"]}\n"
                if event_type == "on_tool_end":
                    yield f"\n 工具:{event["name"]} 执行完毕\n"
                if event_type == "on_chat_model_stream":
                    metadata = event.get("metadata", {})
                    # 摘要模型的输出，不发送给前端
                    if metadata.get("lc_source") == "summarization":
                        continue
                    if event["data"]["chunk"].content:
                        # 累计ai回复消息
                        ai_msg += event["data"]["chunk"].content
                        yield f"{event["data"]["chunk"].content}"
            # 添加窗口记忆ai问题
            c.add_window("ai", ai_msg)
        except Exception as e:
            print(f"同步聊天出现异常:{e}")
            yield "同步聊天出现异常"


# 测试流式输出
async def test_stream(question):
    agent = ChatAgent()
    async for data in agent.chat(question, 1):
        print(data, end="")


if __name__ == "__main__":
    # ---------同步测试----------
    # agent = ChatAgent()
    # rs = agent.chat_invoke("冯有波的邮箱是多少")
    # print(rs)
    # ---------异步测试----------
    import asyncio

    q1 = "客户吕芳是那个国家的，年龄多大"
    q2 = "2023年1月份销售情况"
    asyncio.run(test_stream(q2))
