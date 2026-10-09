from fastapi import APIRouter
from fastapi import Request
from starlette.responses import StreamingResponse
import json
import redis

#创建一个子路由应用程序
chat_router = APIRouter()

client = redis.StrictRedis(host="localhost", port=6379, db=0)
#定义一个聊天接口
@chat_router.get("/chat")
async def chat(question:str, user_id, req:Request):
    key = f"work:{user_id}"
    try:
        if client.get(key):
            #获取word智能体对象
            word_agent = req.app.state.word_agent
            #获取excel智能体对象
            excel_agent = req.app.state.excel_agent
        else:
            # 获取路由智能体返回的结果
            router_agent = req.app.state.router_agent
            rs = router_agent.chat_invoke(question)
            if rs["agent"] == "word_agent":
                # 获取word智能体对象
                agent = req.app.state.word_agent
            elif rs["agent"] == "excel_agent":
                # 获取excel智能体对象
                agent = req.app.state.excel_agent
            else:
                # 获取聊天智能体对象
                agent = req.app.state.chat_agent

        #创建一个异步的流式输出迭代器
        async def generate(question:str):
            try:
                async for c in agent.chat(question, user_id):
                    #流式正在传输，设置done=False表示正在输出
                    data = {"data":c, "done":False}
                    yield f"data:{json.dumps(data)}\n\n"
                #流式输出结束，设置done=True表示关闭
                data = {"data":"", "done":True}
                yield f"data:{json.dumps(data)}\n\n"

            except Exception as e:
                print(f"聊天流式异常：{e}")
                #流式输出结束，设置done=True表示关闭
                data = {"data": "聊天流式异常", "done":True, "error":True}
                yield f"data:{json.dumps(data)}\n\n"
        return StreamingResponse(generate(question), media_type="text/event-stream")
    except Exception as e:
        client.delete(key)
