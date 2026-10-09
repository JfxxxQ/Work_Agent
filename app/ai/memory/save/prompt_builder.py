"""
提示词构建器
"""
class PromptBuilder:

    def __init__(self, window_memory, summary_memory, long_memory, profile_memory, user_id, session_id, question):
        self.window_memory = window_memory
        self.summary_memory = summary_memory
        self.long_memory = long_memory
        self.profile_memory = profile_memory
        self.user_id = user_id
        self.session_id = session_id
        self.question = question

#构建提示词
    def builder(self):
        prompt = "你是一个记忆助手\n"
        #窗口记忆
        w_memory = self.window_memory.load()
        for x in w_memory:
            prompt += f"短期记忆：{x["role"]}:{x["content"]}\n"
        #摘要记忆
        s_memory = self.summary_memory.load_memory(self.session_id)
        prompt += f"摘要记忆：{s_memory}\n"
        #长期记忆
        l_memory = self.long_memory.load_memory(self.user_id, self.question)
        prompt += f"长期记忆：{"\n".join(l_memory)}\n"
        #用户画像
        p_memory = self.profile_memory.load()
        prompt += f"用户画像：{p_memory}\n"
        return prompt