from app.ai.model.my_model import MyModel
from app.ai.tool.word_new_tool import  read_doc_tool, write_doc_tool
from langchain.agents import create_agent
from langchain_core.messages import AIMessageChunk
from app.ai.memory.memory_manager import MemoryManager
from app.ai.memory.save.conversation_manager import ConversationManager


class WordAgent:

    def __init__(self):
        self.model = MyModel.get_local_model()
        self.prompt = self.get_prompt()
        self.tool = self.get_tool()
        self.agent = self.get_agent()
        # 创建redis链接对象
        #self.client = redis.StrictRedis(host="localhost", port=6379, db=0)

    def get_prompt(self):
        self.prompt = """
            你是文档办公助手。
            一：任务流程：
                1. 用户要求对word文档提取摘要生成新word。
                2. 第一步调用 read_doc_tool，传入用户提供的file_path，读取word全部原始文本。
                3. 获取文档全部文本之后，**你自己对文档做摘要处理**：
                    - 精简压缩，不要复制原文大段；
                    - 概括全文核心信息；
                    - 不要编造不存在内容，忠于原文；
                4. 摘要完成后，调用 write_doc_tool：
                    output_title：生成简短相关标题；
                    summary_content：就是你刚刚生成好的摘要文本。
                
            二：规则：
                - 不要在工具内部做摘要，摘要由你自己完成。
                - 先读文档，拿到文档内容，再做摘要，最后写文档。
                - 不要跳过读取文档直接调用写文档工具。
                - 只要内容只允许生成文档相关的内容，不允许生成文档没有的内容
                工具执行结束后，把返回路径整理回复给用户。

            四：调用规则
                1. 用户要求读取word、提取摘要生成新word，必须调用工具 get_create_doc_tool，不要自己生成文档内容。
                3. 不要编造文档内容，全部交给工具读取原始文件。
                4. 工具执行完成之后，把工具返回结果整理回复用户。
        """
        return self.prompt

    def get_tool(self):
        self.tool = [read_doc_tool, write_doc_tool]
        return self.tool

    def get_agent(self):
        self.agent = create_agent(
            model=self.model,
            tools=self.tool,
            system_prompt=self.prompt
        )
        return self.agent

    async def chat(self, question: str, user_id):
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

async def test(question):
    agent = WordAgent()
    async for data in agent.chat(question, 1):
        print(data, end="")


if __name__ == "__main__":
    import asyncio
    user_input = r"这是我的word文档绝对路径D:\AI\home_work\测试模板\test2.docx，请帮我提取重要内容"
    asyncio.run(test(user_input))