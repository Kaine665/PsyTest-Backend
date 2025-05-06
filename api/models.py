from django.db import models
import os
import json
from pymongo import MongoClient

# Create your models here.
USERS_DIR = "api/src/users"

class User:
    def __init__(self, account, password):
        self.account = account
        self.password = password
        
    @staticmethod
    def load(account):
        # 根据账号加载用户
        for file_name in os.listdir(USERS_DIR):
            file_path = os.path.join(USERS_DIR, file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if data.get("account") == account:
                    return User(account=data["account"], password=data["password"])
        return None

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
        
    @staticmethod
    def load(chat_history_id):
        # 只从MongoDB中加载聊天历史
        data = chat_collection.find_one({"chat_history_id": chat_history_id})
        if not data:
            return None
        
        # 移除MongoDB的_id字段
        if '_id' in data:
            del data['_id']
            
        return ChatHistory(
            chat_history_id=data["chat_history_id"],
            user_id=data["user_id"],
            prompt_id=data["prompt_id"],
            patient_id=data["patient_id"],
            update_time=data["update_time"],
            content=data["content"]
        )
            
    @staticmethod
    def load_all_by_user(user_id):
        # 只从MongoDB中加载用户的所有聊天历史
        cursor = chat_collection.find({"user_id": user_id})
        histories = []
        for doc in cursor:
            # 移除MongoDB的_id字段
            if '_id' in doc:
                del doc['_id']
            histories.append(doc)
        
        return histories
            
    def save(self):
        # 只保存到MongoDB
        data_dict = self.__dict__
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
        
    @staticmethod
    def load(patient_id):
        for file_name in os.listdir(PATIENTS_DIR):
            file_path = os.path.join(PATIENTS_DIR, file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if data.get("patient_id") == patient_id:
                    return Patient(
                        patient_id=data["patient_id"],
                        patient_name=data.get("patient_name", ""),
                        patient_introduce=data.get("patient_introduce", ""),
                        prompt=data.get("prompt", "")
                        )
        return None
    
PROMPTS_DIR = "api/src/prompts"
    
class Prompt:
    def __init__(self, prompt_id, prompt_type, prompt):
        self.prompt_id = prompt_id
        self.prompt_type = prompt_type
        self.prompt = prompt
        
    @staticmethod
    def load(prompt_id):
        for file_name in os.listdir(PROMPTS_DIR):
            file_path = os.path.join(PROMPTS_DIR, file_name)
            with open(file_path, 'r', encoding="utf-8") as file:
                data = json.load(file)
                if data.get("prompt_id") == prompt_id:
                    return Prompt(prompt_id=data["prompt_id"], prompt_type=data['prompt_type'], prompt=data["prompt"])
        return None
    
CHARACTER_DIR = "api/src/characters"

    