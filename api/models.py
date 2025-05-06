from django.db import models
import os
import json
from pymongo import MongoClient

# Create your models here.
USERS_DIR = "api/src/users"

from .serializers import UserSerializer, ChatHistorySerializer, PatientSerializer, PromptSerializer

# MongoDB连接设置
MONGO_URI = "mongodb+srv://Kaine:j877413fxt@clusterpsy.pylcmi3.mongodb.net/"
MONGO_DB = "PsyTest"
MONGO_COLLECTION = "chatHistories"

# 初始化MongoDB客户端
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[MONGO_DB]
chat_collection = db[MONGO_COLLECTION]

# 仅为保持兼容性保留此常量，不再用于数据存储
CHAT_HISTORIES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "chat_histories")

class ChatHistory:
    def __init__(self, chat_history_id, user_id, prompt_id, patient_id, update_time, content):
        self.chat_history_id = chat_history_id
        self.user_id = user_id
        self.prompt_id = prompt_id
        self.patient_id = patient_id
        self.update_time = update_time
        self.content = content
        self.type = "chat_history"  # 添加type字段
        
    @staticmethod
    def load(chat_history_id):
        # 只从MongoDB中加载聊天历史
        data = chat_collection.find_one({"chat_history_id": chat_history_id})
        if not data:
            return None
        
        # 移除MongoDB的_id字段
        if '_id' in data:
            del data['_id']
        
        # 确保有type字段
        if 'type' not in data:
            data['type'] = 'chat_history'
        
        # 使用序列化器验证
        serializer = ChatHistorySerializer(data=data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            return ChatHistory(
                chat_history_id=validated_data["chat_history_id"],
                user_id=validated_data["user_id"],
                prompt_id=validated_data["prompt_id"],
                patient_id=validated_data["patient_id"],
                update_time=validated_data["update_time"],
                content=validated_data["content"]
            )
        return None

    def save(self):
        # 序列化并保存到MongoDB
        serializer = ChatHistorySerializer(self)
        data_dict = serializer.data
        chat_collection.update_one(
            {"chat_history_id": self.chat_history_id},
            {"$set": data_dict},
            upsert=True
        )

    def delete(self):
        # 只从MongoDB中删除
        chat_collection.delete_one({"chat_history_id": self.chat_history_id})
        
        # 同时从文件系统中删除(如果存在)
        file_path = os.path.join(CHAT_HISTORIES_DIR, f"chat_history_{self.chat_history_id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)

PATIENTS_DIR = "api/src/patients"

class Patient:
    def __init__(self, patient_id, patient_name, patient_introduce, prompt):
        self.patient_id = patient_id
        self.patient_name = patient_name
        self.patient_introduce = patient_introduce
        self.prompt = prompt
        self.type = "patient"  # 添加type字段
        
    @staticmethod
    def load(patient_id):
        for file_name in os.listdir(PATIENTS_DIR):
            file_path = os.path.join(PATIENTS_DIR, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    # 确保有type字段
                    if 'type' not in data:
                        data['type'] = 'patient'
                        
                    if data.get("patient_id") == patient_id:
                        # 使用序列化器验证
                        serializer = PatientSerializer(data=data)
                        if serializer.is_valid():
                            validated_data = serializer.validated_data
                            return Patient(
                                patient_id=validated_data["patient_id"],
                                patient_name=validated_data.get("patient_name", ""),
                                patient_introduce=validated_data.get("patient_introduce", ""),
                                prompt=validated_data.get("prompt", "")
                            )
                        else:
                            print(f"患者数据验证失败: {serializer.errors}")
            except Exception as e:
                print(f"加载患者数据出错: {str(e)}, 文件: {file_path}")
        return None
    
PROMPTS_DIR = "api/src/prompts"
    
class Prompt:
    def __init__(self, prompt_id, prompt_type, prompt):
        self.prompt_id = prompt_id
        self.prompt_type = prompt_type
        self.prompt = prompt
        self.type = "prompt"  # 添加type字段
        
    @staticmethod
    def load(prompt_id):
        for file_name in os.listdir(PROMPTS_DIR):
            file_path = os.path.join(PROMPTS_DIR, file_name)
            try:
                with open(file_path, 'r', encoding="utf-8") as file:
                    data = json.load(file)
                    # 确保有type字段
                    if 'type' not in data:
                        data['type'] = 'prompt'
                        
                    # 确保有prompt_type字段
                    if 'prompt_type' not in data:
                        data['prompt_type'] = 'default'
                        
                    if data.get("prompt_id") == prompt_id:
                        # 使用序列化器验证
                        serializer = PromptSerializer(data=data)
                        if serializer.is_valid():
                            validated_data = serializer.validated_data
                            return Prompt(
                                prompt_id=validated_data["prompt_id"], 
                                prompt_type=validated_data["prompt_type"], 
                                prompt=validated_data["prompt"]
                            )
                        else:
                            print(f"提示词数据验证失败: {serializer.errors}")
            except Exception as e:
                print(f"加载提示词数据出错: {str(e)}, 文件: {file_path}")
        return None
    
CHARACTER_DIR = "api/src/characters"

    