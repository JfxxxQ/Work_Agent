from fastapi import APIRouter
from starlette.responses import RedirectResponse

#创建一个子路由应用程序
default_router = APIRouter()


#定义一个模拟访问接口
@default_router.get("/")
async def default_page():
    return RedirectResponse(url="/static/chat.html")