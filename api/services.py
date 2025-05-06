from .models import Patient, Prompt, ChatHistory
from .serializers import PatientSerializer, PromptSerializer, ChatHistorySerializer
from .chat_robot import ChatRobot
import os
import json
import datetime
import pytz
import uuid

# 定义用户目录
USERS_DIR = "api/src/users"

class UserService:
    @staticmethod
    def login(account, password):
        for file_name in os.listdir(USERS_DIR):
            file_path = os.path.join(USERS_DIR, file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                # 确保有type字段
                if 'type' not in data:
                    data['type'] = 'user'
                    
                if data.get("account") == account and data.get("password") == password:
                    return {"success": True, "account": account}
        return {"success": False, "msg": "用户名或密码错误"}

class PatientService:
    @staticmethod
    def get_all_patients():
        patients_dir = "api/src/patients"
        patients = []
        
        for file_name in os.listdir(patients_dir):
            file_path = os.path.join(patients_dir, file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                # 确保有type字段
                if 'type' not in data:
                    data['type'] = 'patient'
                patients.append(data)
                
        # 使用序列化器验证和处理
        serialized_patients = []
        for patient_data in patients:
            serializer = PatientSerializer(data=patient_data)
            if serializer.is_valid():
                serialized_patients.append(serializer.data)
                
        return serialized_patients

class PromptService:
    @staticmethod
    def get_all_prompts():
        prompts_dir = "api/src/prompts"
        prompts = []
        
        for file_name in os.listdir(prompts_dir):
            file_path = os.path.join(prompts_dir, file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                # 确保有type字段
                if 'type' not in data:
                    data['type'] = 'prompt'
                prompts.append(data)
                
        # 使用序列化器验证和处理
        serialized_prompts = []
        for prompt_data in prompts:
            serializer = PromptSerializer(data=prompt_data)
            if serializer.is_valid():
                serialized_prompts.append(serializer.data)
                
        return serialized_prompts

class ChatService:
    @staticmethod
    def get_chat_histories_by_user_id(user_id):
        from pymongo import MongoClient
        
        # MongoDB连接设置
        MONGO_URI = "mongodb+srv://Kaine:j877413fxt@clusterpsy.pylcmi3.mongodb.net/"
        MONGO_DB = "PsyTest"
        MONGO_COLLECTION = "chatHistories"

        # 初始化MongoDB客户端
        mongo_client = MongoClient(MONGO_URI)
        db = mongo_client[MONGO_DB]
        chat_collection = db[MONGO_COLLECTION]
        
        # 查询MongoDB获取用户的聊天历史
        chats_cursor = chat_collection.find({"user_id": user_id})
        chats = []
        
        # 处理查询结果
        for chat in chats_cursor:
            # 移除MongoDB的_id字段
            if '_id' in chat:
                del chat['_id']
                
            # 确保有type字段
            if 'type' not in chat:
                chat['type'] = 'chat_history'
                
            # 使用序列化器验证
            serializer = ChatHistorySerializer(data=chat)
            if serializer.is_valid():
                chats.append(serializer.data)
        
        return chats
        
    @staticmethod
    def get_chat_history(chat_history_id):
        # 通过模型加载聊天历史
        chat_history = ChatHistory.load(chat_history_id)
        if not chat_history:
            return None
            
        # 序列化返回
        serializer = ChatHistorySerializer(chat_history)
        return serializer.data
    
    @staticmethod
    def create_chat_history(user_id, prompt_id, patient_id):
        chat_history_id = str(uuid.uuid4())
        current_time = datetime.datetime.now(pytz.timezone('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S")
        
        # 创建初始聊天历史
        chat_history = ChatHistory(
            chat_history_id=chat_history_id,
            user_id=user_id,
            prompt_id=prompt_id,
            patient_id=patient_id,
            update_time=current_time,
            content=[]
        )
        
        # 保存到MongoDB
        chat_history.save()
        
        # 序列化返回
        serializer = ChatHistorySerializer(chat_history)
        return serializer.data
    
    @staticmethod
    def delete_chat_history(chat_history_id):
        chat_history = ChatHistory.load(chat_history_id)
        if chat_history:
            chat_history.delete()
            return True
        return False
    
    @staticmethod
    def chat(chat_history_id, user_message):
        chat_history = ChatHistory.load(chat_history_id)
        if not chat_history:
            return {"success": False, "msg": "聊天历史不存在"}
            
        patient = Patient.load(chat_history.patient_id)
        if not patient:
            return {"success": False, "msg": "病人信息不存在"}
            
        prompt = Prompt.load(chat_history.prompt_id)
        if not prompt:
            return {"success": False, "msg": "提示词信息不存在"}
        
        # 添加用户消息
        chat_history.content.append({"role": "user", "content": user_message})
        
        # 使用ChatRobot生成回复
        chat_robot = ChatRobot(patient.prompt)
        assistant_message = chat_robot.chat(chat_history.content)
        
        # 添加助手回复
        chat_history.content.append({"role": "assistant", "content": assistant_message})
        
        # 更新时间
        current_time = datetime.datetime.now(pytz.timezone('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S")
        chat_history.update_time = current_time
        
        # 保存更新后的聊天历史
        chat_history.save()
        
        return {
            "success": True, 
            "message": assistant_message,
            "chat_history": ChatHistorySerializer(chat_history).data
        }


class ChatRobotService:
    @staticmethod
    def process_message(chat_history_id, user_message):
        # 获取聊天历史
        chat_history = ChatHistory.load(chat_history_id)
        if not chat_history:
            return {"success": False, "msg": "聊天历史不存在"}
            
        # 获取病人信息
        patient = Patient.load(chat_history.patient_id)
        if not patient:
            return {"success": False, "msg": "病人信息不存在"}
            
        # 获取提示词
        prompt = Prompt.load(chat_history.prompt_id)
        if not prompt:
            return {"success": False, "msg": "提示词信息不存在"}
        
        try:
            # 使用ChatRobot生成回复
            company = "openrouter"  # 默认使用openrouter，您可以根据需要修改
            model = "anthropic/claude-3-opus"  # 默认使用claude-3，您可以根据需要修改
            
            # 创建ChatRobot实例
            from .chat_robot import ChatRobot
            chat_robot = ChatRobot(company, model, patient.prompt, chat_history.content)
            
            # 添加用户消息并生成AI回复
            chat_robot.addUserMessage(user_message)
            ai_response = chat_robot.generateAiResponse()
            
            return {"success": True, "data": ai_response}
        except Exception as e:
            return {"success": False, "msg": f"生成AI回复时出错: {str(e)}"}
    
    @staticmethod
    def get_feedback(chat_history_id, user_message):
        # 获取聊天历史
        chat_history = ChatHistory.load(chat_history_id)
        if not chat_history:
            return {"success": False, "msg": "聊天历史不存在"}
        
        try:
            # 使用ChatRobot生成督导反馈
            company = "openrouter"  # 默认使用openrouter，您可以根据需要修改
            model = "anthropic/claude-3-opus"  # 默认使用claude-3，您可以根据需要修改
            
            # 督导提示词 - 请根据实际情况修改
            feedback_prompt = "你是一位心理咨询督导师，请对咨询师的回应给予专业的指导和建议。"
            
            # 创建ChatRobot实例
            from .chat_robot import ChatRobot
            chat_robot = ChatRobot(company, model, feedback_prompt)
            
            # 构建消息内容
            user_content = f"咨询师对来访者说：{user_message}\n请给予专业督导意见。"
            chat_robot.addUserMessage(user_content)
            
            # 生成督导反馈
            feedback = chat_robot.generateAiResponse()
            
            # 如果反馈内容为"继续"，则不显示督导反馈
            if feedback.strip() == "继续":
                return {"success": True, "data": "继续"}
            
            return {"success": True, "data": feedback}
        except Exception as e:
            return {"success": False, "msg": f"生成督导反馈时出错: {str(e)}"}