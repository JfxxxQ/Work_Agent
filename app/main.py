from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from app.web.chat_router.chat_router import chat_router
from app.web.system_router.system_router import system_router
from app.web.default_page_router.default_page_router import default_router
import uvicorn
from app.ai.agent.chat_agent import ChatAgent
from contextlib import asynccontextmanager #一个装饰器
from app.ai.agent.work_agent.word_agent import WordAgent
from app.ai.agent.work_agent.excel_agent import ExcelAgent
from app.ai.agent.router_agent import RouterAgent
#配置异步的上下文管理器
@asynccontextmanager
async def contenttextManger(app:FastAPI):
    #创建聊天智能体
    app.state.chat_agent = ChatAgent() #把chat_agent设置为全局变量
    #创建word智能体
    app.state.word_agent = WordAgent()
    #创建excel智能体
    app.state.excel_agent = ExcelAgent()
    #创建路由智能体
    app.state.router_agent = RouterAgent()
    print("创建聊天智能体")
    print("创建word智能体")
    print("创建excel智能体")
    print("创建路由智能体")
    yield
    print("销毁聊天智能体")
    print("创建word智能体")
    print("创建excel智能体")
    print("销毁路由智能体")
    app.state.chat_agent = None
    app.state.word_agent = None
    app.state.excel_agent = None
    app.state.router_agent = None

#创建一个fastApi应用程序
app = FastAPI(lifespan=contenttextManger)
#添加子路由或者注册子路由
app.include_router(chat_router)
app.include_router(system_router)
app.include_router(default_router)

#配置静态资源文件
app.mount("/static", StaticFiles(directory="./html"), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)