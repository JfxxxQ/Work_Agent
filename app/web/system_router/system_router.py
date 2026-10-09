from fastapi import APIRouter
import ast
import random
from app.ai.tool.send_email_tool import send_email_tool
from app.ai.tool.mysql_tool import mysql_tool
import redis

client = redis.StrictRedis(host="localhost", port=6379, db=0)

#创建一个子路由应用程序
system_router = APIRouter()

#定义一个发送验证码接口
@system_router.get("/sendCode")
async def send_code(email: str):
    try:
        #生成一个4位数的随机数
        code = random.randint(1000, 9999)
        #发送验证码
        rs = send_email_tool.invoke({
            "to":email,
            "subject":"AI多智能体平台系统验证码",
            "content":f"你收到的验证码是：{code}，请在1分钟内使用"
        })
        if rs == "邮件发送成功":
            key = f"code:{email}"
            client.set(key, code, ex=60)
            return {"code": 200, "msg": "验证码发送成功"}
        else:
            return {"code": 500, "msg": "验证码发送失败"}
    except Exception as e:
        print(f"发送验证码失败：{e}")
        return {"code": 500, "msg": "验证码发送失败"}
#定义一个登录接口
@system_router.get("/login")
async def login(email:str, code:str):
    #------------------1 验证邮箱是否是数据库的----------------------
    try:
        sql = f"select user_id, email from user_info where email = '{email}'"
        rs = mysql_tool.invoke({"sql": sql})
        print(f"rs:{rs}")
        if rs == "()":
            return {"code": 500, "msg": "邮箱不存在"}
        else:
        #--------------2 验证验证码是否正确
            key = f"code:{email}"
            code_redis = client.get(key)
            print(f"验证码：{code_redis}")
            if not code_redis:
                return {"code": 500, "msg": "验证码已过期"}
            elif code_redis.decode() == code:
                #类型转换
                data = ast.literal_eval(rs)
                user_id = data[0][0]
                return {"code": 200, "msg": "登录成功", "user_id": user_id}
            else:
                return {"code": 500, "msg": "验证码不正确"}
    except Exception as e:
        print(f"登录失败：{e}")
        return {"code": 500, "msg": "登录失败"}