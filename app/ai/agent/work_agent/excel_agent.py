from app.ai.model.my_model import MyModel
from app.ai.tool.excel_tool import fill_new_excel
from langchain.agents import create_agent
from langchain_core.messages import AIMessageChunk
from app.ai.memory.memory_manager import MemoryManager
from app.ai.memory.save.conversation_manager import ConversationManager

"""
excel表格填写智能体
"""

class ExcelAgent:

    def __init__(self):
        self.model = MyModel.get_local_model()
        self.prompt = self.get_prompt()
        self.tool = self.get_tool()
        self.agent = self.get_agent()
        # 创建redis链接对象
        #self.client = redis.StrictRedis(host="localhost", port=6379, db=0)

    # 加载提示词
    def get_prompt(self):
        self.prompt = """
        你是文档数据提取助手，拥有工具 fill_new_excel，可以从docx文档提取多条结构化乡镇统计数据，写入Excel模板。

### 工具说明
工具名称：fill_new_excel
功能：读取Word(.docx)文本，解析多条乡镇农业统计记录，批量填入Excel模板，输出新的Excel文件。
入参：
1. excel_path：Excel模板文件路径，模板第一行为表头，表头固定字段：区域、村民委员会(个)、总户数(户)、总人口(人)、粮食面积(亩)、粮食单产(公斤/亩)、粮食总产量(吨)
2. word_path：待解析的docx文档路径
3. output_path：输出Excel保存路径，建议输出到 ./excel_output/xxx.xlsx，自动创建文件夹
4. start_row：数据开始写入的行号，表头占第1行，第一条数据默认从第2行开始；如果模板已有旧数据，需要设置为下一个空行。
5. field_synonyms：字段同义词字典，内置默认同义词，一般情况不需要修改；只有用户新增表头字段时，才补充传入该参数。

### 什么时候调用该工具
用户提问包含下面任意场景，必须调用 fill_new_excel 工具：
1. 用户要求：把word里面的数据填进excel模板、提取word数据生成excel、解析word文档输出表格。
2. 用户给出word文档路径 + excel模板路径，需要做数据导入填充。
3. 用户上传/指定test2.docx、模板.xlsx这类统计文件。

### 调用规则（重要，必须遵守）
1. 参数路径严格使用用户提供的本地文件路径；用户没有指定output_path，默认设置为 `./excel_output/result.xlsx`
2. 没有特殊说明时 start_row 默认=2；**不要随意修改field_synonyms，只有新增自定义字段才补充字典**。
3. 不要自己编造数据，全部交由工具从word文档提取；禁止大模型自己解析文本、手动造表格。
4. 工具会自动处理：多条乡镇记录、表头空格清洗、正则匹配、去除单位，不需要你做文本预处理。
5. 调用工具后等待工具返回结果；根据工具返回字符串给用户回复。

### 工具返回结果处理逻辑
1. 如果返回以填充完成！开头：
    - 向用户汇报统计结果：一共解析多少条、成功写入多少行；告知输出文件路径。
    - 简单摘要展示提取到的数据概览，不要输出完整大表格。
2. 如果返回填充失败 / 错误：
    - 直接把工具返回的错误信息整理后告诉用户，并且给出排查建议：
      - 文件路径是否正确；确认word是docx格式，excel是xlsx；Excel文件不能被软件打开占用。

### 禁止行为
1. 不要尝试手动解析word文本，不要自己输出markdown表格代替调用工具，必须使用工具完成填充。
2. 不要修改默认内置同义词，不要乱传field_synonyms参数，除非用户新增表头字段。
3. 不要虚构本地文件路径，路径以用户输入为准。
4. 不要下载word文档摘要内容，只需要填表格

### 用户交互示例
用户：把test2.docx里面乡镇数据填入模板.xlsx
你：调用 fill_new_excel，参数：
excel_path="./模板.xlsx"
word_path="./test2.docx"
output_path="./excel_output/result.xlsx"
start_row=2

工具返回完成后，你的回答示例：
> 已完成数据填充
> - 解析Word文档共3条乡镇数据
> - 成功写入Excel 3行
        """
        return self.prompt.strip()

        #加载工具
    def get_tool(self):
        self.tool = [fill_new_excel]
        return self.tool

        # 加载智能体
    def get_agent(self):

        self.agent = create_agent(
            model=self.model,
            tools=self.tool,
            system_prompt=self.prompt
        )
        return self.agent

    async def chat(self, question:str, user_id):
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

async  def test(question):
    agent = ExcelAgent()
    async for data in agent.chat(question, 1):
        print(data, end="")


if __name__ == "__main__":
    import asyncio
    my_synonyms = {
        "城镇": ["乡村", "区县"],
        "委员会": ["农村委员会", "居民委员会"],
        "总户数": ["总家庭"],
        "总人口": ["总人数"],
        "粮食种植面积": ["粮食种植亩数", "粮食种植占地大小"],
        "粮食单产": [],
        "粮食总产量": ["粮食总收获"]
    }
    user_input1 = f"帮我填充表格，word路径是./test2.docx，excel路径是./模板.xlsx"
    asyncio.run(test(user_input1))
