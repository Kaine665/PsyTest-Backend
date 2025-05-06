from .database import MongoDatabase
import json

# 创建数据库实例
mongo_db = MongoDatabase()

class User:
    def __init__(self, account, password):
        self.account = account
        self.password = password
        
    @staticmethod
    def load(account):
        # 根据账号加载用户
        user_data = mongo_db.find_one('users', {'account': account})
        if user_data:
            return User(account=user_data["account"], password=user_data["password"])
        return None

    def save(self):
        # 保存或更新用户
        mongo_db.update_one('users', {'account': self.account}, 
                           {'account': self.account, 'password': self.password}, 
                           upsert=True)
    
    def delete(self):
        # 删除用户
        mongo_db.delete_one('users', {'account': self.account})


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
        # 根据ID加载聊天历史
        data = mongo_db.find_one('chat_histories', {'chat_history_id': chat_history_id})
        if not data:
            return None
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
        # 查询用户的所有聊天历史
        histories = []
        cursor = mongo_db.find('chat_histories', {'user_id': user_id})
        for data in cursor:
            histories.append(data)
        return histories
            
    def save(self):
        # 保存或更新聊天历史
        mongo_db.update_one('chat_histories', 
                           {'chat_history_id': self.chat_history_id}, 
                           self.__dict__, 
                           upsert=True)
    
    def delete(self):
        # 删除聊天历史
        mongo_db.delete_one('chat_histories', {'chat_history_id': self.chat_history_id})


class Patient:
    def __init__(self, patient_id, patient_name, patient_introduce, prompt):
        self.patient_id = patient_id
        self.patient_name = patient_name
        self.patient_introduce = patient_introduce
        self.prompt = prompt
        
    @staticmethod
    def load(patient_id):
        # 根据ID加载患者
        data = mongo_db.find_one('patients', {'patient_id': patient_id})
        if data:
            return Patient(
                patient_id=data["patient_id"],
                patient_name=data.get("patient_name", ""),
                patient_introduce=data.get("patient_introduce", ""),
                prompt=data.get("prompt", "")
            )
        return None
    
    @staticmethod
    def load_all():
        # 加载所有患者
        patients = []
        cursor = mongo_db.find('patients', {})
        for data in cursor:
            patients.append(data)
        return patients
    
    def save(self):
        # 保存或更新患者信息
        mongo_db.update_one('patients', 
                           {'patient_id': self.patient_id}, 
                           self.__dict__, 
                           upsert=True)
    
    def delete(self):
        # 删除患者
        mongo_db.delete_one('patients', {'patient_id': self.patient_id})
    
    
class Prompt:
    def __init__(self, prompt_id, prompt_type, prompt):
        self.prompt_id = prompt_id
        self.prompt_type = prompt_type
        self.prompt = prompt
        
    @staticmethod
    def load(prompt_id):
        # 根据ID加载提示
        data = mongo_db.find_one('prompts', {'prompt_id': prompt_id})
        if data:
            return Prompt(
                prompt_id=data["prompt_id"], 
                prompt_type=data['prompt_type'], 
                prompt=data["prompt"]
            )
        return None
    
    @staticmethod
    def load_all():
        # 加载所有提示
        prompts = []
        cursor = mongo_db.find('prompts', {})
        for data in cursor:
            prompts.append(data)
        return prompts
    
    def save(self):
        # 保存或更新提示
        mongo_db.update_one('prompts', 
                           {'prompt_id': self.prompt_id}, 
                           self.__dict__, 
                           upsert=True)
    
    def delete(self):
        # 删除提示
        mongo_db.delete_one('prompts', {'prompt_id': self.prompt_id})

    