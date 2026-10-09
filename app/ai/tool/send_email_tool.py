from dotenv import load_dotenv
import os
from pydantic import BaseModel,Field
from langchain.tools import tool
from email.mime.text import MIMEText
import smtplib
"""
用pydantic 封装邮件工具需要的参数
"""
class EmailParams(BaseModel):
    #... 参数必填，description 必须描述准确，否则无法调用
    to:str = Field(...,description="收件人邮箱")
    subject:str = Field(...,description="邮件主题")
    content:str = Field(...,description="邮件内容")

#读取配置文件
load_dotenv()

@tool("send_email_tool",args_schema=EmailParams)
def send_email_tool(to:str,subject:str,content:str)->str:
    """
       功能描述：发送邮件，发送信息，发送通知
      """

    try:
        #读取邮件配置
        host = os.getenv("EMAIL_HOST")
        user = os.getenv("EMAIL_USER")
        password = os.getenv("EMAIL_PASSWORD")
        port = os.getenv("EMAIL_PORT")
        if not host or not user or not password or not port:
            return "请检查邮件配置"

        #1 创建邮件对象，并引入正文
        msg = MIMEText(content)
        #2 收件人
        msg["To"] = to
        #3 标题
        msg["Subject"] = subject
        #4 发件人
        msg["From"] = user
        #5 登录邮件服务器
        with smtplib.SMTP_SSL(host,int(port) )as smtp:
            #登录
             smtp.login(user,password)
            #发送邮件
             smtp.sendmail(user,to,msg.as_string())
        return "邮件发送成功"
    except Exception as e:
        print(f"出现异常{e}")
        return "发送邮件出现异常了"
if __name__=="__main__":
    rs=send_email_tool.invoke({
        "to":"767920412@qq.com",
        "subject":"测试邮件",
        "content":"测试邮件内容"
    })
    print(rs)

