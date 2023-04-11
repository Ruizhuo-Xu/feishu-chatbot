import openai

class Chat:
    def __init__(self,conversation_list=[]) -> None:
        # 初始化对话列表，可以加入一个key为system的字典，有助于形成更加个性化的回答
        self.conversation_list = [{'role':'system','content':'你是一个非常友善的助手'}]
		# self.conversation_list = []
        self.recv_buffer = []
    
    # 打印对话
    def get_answer(self,msg_list):
        for msg in msg_list:
            if msg['role'] == 'user':
                # print(f"\U0001f47b: {msg['content']}\n")
                return {'text': f"\U0001f47b: {msg['content']}\n"}
            else:
                # print(f"\U0001f47D: {msg['content']}\n")
                return {'text': f"\U0001f47D: {msg['content']}\n"}

    def reset(self):
        self.conversation_list = [{'role':'system','content':'你是一个非常友善的助手'}]

    def set_character(self, idx, prompt=None):
        if idx == '1':
            self.conversation_list = [{'role':'system','content':'你是一个非常友善的助手'}]
        elif idx == '2':
            self.conversation_list = [{'role':'system','content':'你是一个资深的程序员'}]
        elif idx == '3':
            self.conversation_list = [{'role':'system','content':'你是一个温柔善良的小姐姐'}]
        elif idx == '4':
            self.conversation_list = [{'role':'system','content':'你是一个有礼貌的绅士'}]
        else:
            assert prompt is not None, "PLZ offer promt!"
            self.conversation_list = [{'role':'system','content':prompt}]

        return self.conversation_list[0]['content']


    # 提示chatgpt
    def ask(self,prompt):
        self.conversation_list.append({"role":"user","content":prompt})
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo",messages=self.conversation_list)
        answer = response.choices[0].message['content']
        # 下面这一步是把chatGPT的回答也添加到对话列表中，这样下一次问问题的时候就能形成上下文了
        self.conversation_list.append({"role":"assistant","content":answer})
        # answer = self.get_answer(self.conversation_list)
        ret = {'text': f"\U0001f47D: {answer}\n"}
        return ret
