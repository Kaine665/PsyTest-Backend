class ChatRobot:
    # 参数 company, model, prompt, chat_history(非必须) 
    def __init__(self, company, model, prompt, chat_history=None):
        from openai import OpenAI
        self.company = company
        self.model = model
        self.prompt = {"role":"system","content":prompt}
        self.messages = [self.prompt]
        self.chat_history = chat_history
        
        if chat_history:
            for message in chat_history:
                self.messages.append(message)
                
        # 使用 match 语句选择不同的API客户端
        match company:
            case "deepseek":
                from openai import OpenAI
                self.client = OpenAI(api_key="sk-a7e6b203645d4da1b12e0b598695c893", base_url="https://api.deepseek.com")
            case "openai":
                from openai import OpenAI
                self.client = OpenAI(api_key="sk-sWJ3obe1tZi7WaNvf7QRFFu1dkhhBgvTCImJKnycMfT3BlbkFJQUAF4n92f-Fy9K751wsNV4oj7AXHGf0LzshQnyKpYA")  # 请替换为你的OpenAI API密钥
            case "openrouter":
                from openai import OpenAI
                self.client = OpenAI(api_key="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", base_url="https://openrouter.ai/api/v1")
        
    def addUserMessage(self, userInput):
        self.messages.append({"role": "user", "content": userInput})
        
    def generateAiResponse(self):
        # 使用 match 语句根据公司调用不同的API方法
        match self.company:
            case "deepseek":
                # 适用于 deepseek 的 chat.completions.create 方法
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    stream=False,
                    temperature=1
                )
                content = response.choices[0].message.content
            case "openai":
                # 适用于 openai 的 responses.create 方法
                response = self.client.responses.create(
                    model=self.model,
                    input=self.messages
                )
                content = response.output_text
            case "openrouter":
                # 适用于 openrouter 的 chat.completions.create 方法
                response = self.client.chat.completions.create(
                    model= self.model,
                    messages=self.messages
                )
                content = response.choices[0].message.content

        self.messages.append({"role": "assistant", "content": content})
        return content
    
    def getPrompt(self):
        return self.prompt
    
    def getChatHistory(self):
        return self.messages[1:]