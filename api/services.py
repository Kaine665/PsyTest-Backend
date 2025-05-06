from .models import User, ChatHistory, Patient, Prompt
from .chat_robot import ChatRobot
from jinja2 import Template 
import datetime
import pytz

class UserController:
    @staticmethod
    def login(account, password):
        user = User.load(account)
        if not user:
            return {"success": False, "msg": "用户不存在"}
        if user.password != password:
            return {"success": False, "msg": "密码错误"}
        return {"success": True, "msg": "登录成功"}
    
    @staticmethod
    def register(account, password):
        # 检查用户是否已存在
        existing_user = User.load(account)
        if existing_user:
            return {"success": False, "msg": "用户已存在"}
        # 创建新用户
        user = User(account=account, password=password)
        user.save()
        return {"success": True, "msg": "注册成功"}
    
class ChatHistoryController:
    @staticmethod
    def get_history(chat_history_id):
        chat_history = ChatHistory.load(chat_history_id)
        if not chat_history:
            return {"success": False, "msg": "未找到聊天记录"}
        return {"success": True, "data": chat_history.__dict__}
    
    @staticmethod
    def get_histories_by_user(user_id):
        histories = ChatHistory.load_all_by_user(user_id)
        return {"success": True, "data": histories}
    
    @staticmethod
    def save_history(data):
        # 新建chat_history时设置北京时间
        beijing_tz = pytz.timezone("Asia/Shanghai")
        now_str = datetime.datetime.now(beijing_tz).strftime("%Y.%m.%d  %H:%M")
        data["update_time"] = now_str
        chat_history = ChatHistory(**data)
        chat_history.save()
        return {"success": True, "msg": "保存成功"}
    
    @staticmethod
    def delete_history(chat_history_id):
        chat_history = ChatHistory.load(chat_history_id)
        if not chat_history:
            return {"success": False, "msg": "未找到聊天记录"}
        try:
            chat_history.delete()
            return {"success": True, "msg": "删除成功"}
        except Exception as e:
            return {"success": False, "msg": f"删除失败: {str(e)}"}
    
    @staticmethod
    def append_messages(chat_history_id, messages_to_send):
        chat_history = ChatHistory.load(chat_history_id)
        if not chat_history:
            return {"success": False, "msg": "未找到聊天记录"}
        if not hasattr(chat_history, "content") or not isinstance(chat_history.content, list):
            return {"success": False, "msg": "聊天记录内容格式错误"}
        chat_history.content.extend(messages_to_send)
        # 每次追加消息时更新时间（北京时间）
        beijing_tz = pytz.timezone("Asia/Shanghai")
        chat_history.update_time = datetime.datetime.now(beijing_tz).strftime("%Y.%m.%d  %H:%M")
        chat_history.save()
        return {"success": True, "msg": "追加消息成功"}
    
class PatientController:
    @staticmethod
    def get_patient(patient_id):
        patient = Patient.load(patient_id)
        if not patient:
            return {"success": False, "msg": "未找到目标角色信息"}
        return {"success": True, "data": patient.__dict__}

    @staticmethod
    def get_all_patients():
        patients = Patient.load_all()
        if not patients:
            return {"success": False, "msg": "未找到角色信息"}
        return {"success": True, "data": patients}
        
class PromptController:
    @staticmethod
    def get_prompt(prompt_id):
        prompt = Prompt.load(prompt_id)
        if not prompt:
            return {"success": False, "msg": "未找到目标练习类型"}
        return {"success": True, "data": prompt.__dict__}

    @staticmethod
    def get_all_prompts():
        prompts = Prompt.load_all()
        if not prompts:
            return {"success": False, "msg": "未找到练习类型信息"}
        return {"success": True, "data": prompts}
    
class ChatRobotService:
    @staticmethod
    def process_message(chat_history_id, input_value):
        try:
            chat_history = ChatHistory.load(chat_history_id)
            if not chat_history:
                return {"success": False, "msg": "未找到聊天记录"}
            filtered_history = [msg for msg in chat_history.content if msg["role"] != "feedback"]
            prompt_id = chat_history.prompt_id
            patient_id = chat_history.patient_id

            # 载入 Prompt
            prompt_obj = Prompt.load(prompt_id)
            if not prompt_obj:
                return {"success": False, "msg": "未找到Prompt"}

            # 载入 Patient
            patient = Patient.load(patient_id)
            if not patient:
                return {"success": False, "msg": "未找到角色信息"}

            # 进行jinja2模板合成
            template = Template(prompt_obj.prompt)
            # 这里假设模板内用到的字段有姓名、问题描述、聊天记录，可按需调整
            prompt_text = template.render(
                姓名=patient.patient_name,
                问题描述=patient.prompt,
                聊天记录="无"  # 可以根据实际情况填写
            )
            ai_robot = ChatRobot(company="openrouter", model="openai/gpt-4.1", prompt=prompt_text, chat_history=filtered_history)
            ai_robot.addUserMessage(input_value)
            ai_response = ai_robot.generateAiResponse()
            return {"success": True, "data": ai_response}
        except Exception as e:
            return {"success": False, "msg": f"AI回复服务异常: {str(e)}"}

    @staticmethod
    def get_feedback(chat_history_id, input_value):
        try:
            chat_history = ChatHistory.load(chat_history_id)
            if not chat_history:
                return {"success": False, "msg": "未找到聊天记录"}
            filtered_history = [msg for msg in chat_history.content if msg["role"] != "feedback"]
            
            # 从数据库获取督导反馈的 prompt
            feedback_prompt = Prompt.load("督导-单句反馈")
            if not feedback_prompt:
                return {"success": False, "msg": "未找到督导反馈提示"}
            
            ai_robot = ChatRobot(company="openrouter", model="google/gemini-2.5-pro-preview-03-25", prompt=feedback_prompt.prompt, chat_history=filtered_history)
            ai_robot.addUserMessage(input_value)
            ai_response = ai_robot.generateAiResponse()
            return {"success": True, "data": ai_response}
        except Exception as e:
            return {"success": False, "msg": f"AI反馈服务异常: {str(e)}"}
        
    @staticmethod
    def append_messages(chat_history_id, messages_to_send):
        chat_history = ChatHistory.load(chat_history_id)
        if not chat_history:
            return {"success": False, "msg": "未找到聊天记录"}
        if not hasattr(chat_history, "content") or not isinstance(chat_history.content, list):
            return {"success": False, "msg": "聊天记录内容格式错误"}
        chat_history.content.extend(messages_to_send)
        chat_history.save()
        return {"success": True, "msg": "追加消息成功"}