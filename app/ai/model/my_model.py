from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

#读取配置文件
load_dotenv()

"""
模型封装：
目的：方便后期代码维护和更改，已经实例对象的资源创建
"""
class MyModel:
    #在线大模型的私有属性
    _line_model = None
    #本地大模型的私有属性
    _local_model = None
    # 单例模型或者懒加载

    #在线大模型的封装
    @staticmethod
    def get_line_model():
        #第一次创建模型对象
        if MyModel._line_model is None:
            MyModel._line_model = ChatOpenAI(
                model=os.getenv("MODEL_LINE_NAME"),
                api_key=os.getenv("DASHSCOPE_API_KEY"),  # 密钥
                extra_body={
                    "enable_thinking": False
                },
                streaming=True,  # 是否流式返回
            )
        #返回模型对象
        return MyModel._line_model

    #本地大模型的封装
    @staticmethod
    def get_local_model():
        #第一次创建模型对象
        if MyModel._local_model is None:
            MyModel._local_model = ChatOpenAI(
                model=os.getenv("MODEL_LOCAL_NAME"),
                base_url=os.getenv("LOCAL_URL"),
                api_key="ddd",
                streaming=True,#是否流式返回
            )
        #返回模型对象
        return MyModel._local_model


if __name__ == "__main__":
    model = MyModel.get_local_model()
    rs = model.invoke(input="你好")
    print(rs)