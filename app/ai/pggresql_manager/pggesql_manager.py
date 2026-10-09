from langgraph.checkpoint.postgres import PostgresSaver
from dotenv import load_dotenv
import os

load_dotenv()
url = os.getenv("PG_URL")
pg = PostgresSaver.from_conn_string(url)
#获取上下管理器对象
pg_saver = pg.__enter__()
#创建数据库和表
pg_saver.setup()