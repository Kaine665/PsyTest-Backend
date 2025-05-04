from .models import User, ChatHistory,Patient, Prompt
from .chat_robot import ChatRobot
from jinja2 import Template 
import datetime


class UserController:
    @staticmethod
    def login(account, password):
        user = User.load(account)
        if not user:
            return {"success": False, "msg": "用户不存在"}
        if user.password != password:
            return {"success": False, "msg": "密码错误"}
        return {"success": True, "msg": "登录成功"}
    
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
        # 新建chat_history时设置时间
        now_str = datetime.datetime.now().strftime("%Y.%m.%d  %H:%M")
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
        # 每次追加消息时更新时间
        chat_history.update_time = datetime.datetime.now().strftime("%Y.%m.%d  %H:%M")
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
        from .models import PATIENTS_DIR, Patient
        import os, json

        patients = []
        try:
            for file_name in os.listdir(PATIENTS_DIR):
                file_path = os.path.join(PATIENTS_DIR, file_name)
                with open(file_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    patients.append(data)
            return {"success": True, "data": patients}
        except Exception as e:
            print(f"读取病人数据出错: {str(e)}")
            return {"success": False, "msg": f"读取病人数据出错: {str(e)}"}
        
class PromptController:
    @staticmethod
    def get_prompt(prompt_id):
        prompt = Prompt.load(prompt_id)
        if not prompt:
            return {"success": False, "msg": "未找到目标练习类型"}
        return {"success": True, "data": prompt.__dict__}

    @staticmethod
    def get_all_prompts():
        from .models import PROMPTS_DIR
        import os, json

        prompts = []
        try:
            for file_name in os.listdir(PROMPTS_DIR):
                file_path = os.path.join(PROMPTS_DIR, file_name)
                with open(file_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    prompts.append(data)
            return {"success": True, "data": prompts}
        except Exception as e:
            print(f"读取提示数据出错: {str(e)}")
            return {"success": False, "msg": f"读取提示数据出错: {str(e)}"}
    
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
            from .models import PROMPTS_DIR
            import os, json
            feedback_prompt_path = os.path.join(PROMPTS_DIR, "督导-单句反馈-prompt.json")
            with open(feedback_prompt_path, "r", encoding="utf-8") as f:
                feedback_prompt = json.load(f)["prompt"]
            ai_robot = ChatRobot(company="openrouter", model="google/gemini-2.5-pro-preview-03-25", prompt=feedback_prompt, chat_history=filtered_history)
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