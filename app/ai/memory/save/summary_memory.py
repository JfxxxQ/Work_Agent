from app.ai.pggresql_manager.pggresql_pool import pool

"""
摘要记忆，记忆对话的摘要记忆
"""
class SummaryMemory:

    def __init__(self):
        self.pool = pool
    #添加记忆
    def add_memory(self,session_id,summary):
      with self.pool.connection() as con:
          with con.cursor() as cursor:
              sql = f"insert into conversation_summary (session_id,summary) VALUES('{session_id}','{summary}') on conflict (session_id) do UPDATE  set summary = EXCLUDED.summary, update_time = NOW(),create_time = NOW()"
              #执行sql
              cursor.execute(sql)
              #事务提交
              con.commit()
    #查询记忆
    def load_memory(self,session_id):
        with self.pool.connection() as con:
            with con.cursor() as cursor:
                sql = f"select summary from  conversation_summary where session_id='{session_id}' "
                # 执行sql
                cursor.execute(sql)
                # 获取结果
                rs = cursor.fetchone()
                if rs:
                    return rs[0]
                else:
                    return ""

if __name__ == "__main__":
    s = SummaryMemory()
    s.add_memory("1","我用langchain开发智能体22")
    rs = s.load_memory("1")
    print(f"结果:{rs}")