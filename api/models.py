from django.db import models
import os
import json

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

CHAT_HISTORIES_DIR = "api/src/chat_histories"

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
        file_path = os.path.join(CHAT_HISTORIES_DIR, f"chat_history_{chat_history_id}.json")
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'r', encoding="utf-8") as file:
            data = json.load(file)
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
        histories = []
        for file_name in os.listdir(CHAT_HISTORIES_DIR):
            file_path = os.path.join(CHAT_HISTORIES_DIR, file_name)
            with open(file_path, 'r', encoding="utf-8") as file:
                data = json.load(file)
                if data.get("user_id") == user_id:
                    histories.append(data)
        return histories
            
    def save(self):
        file_path = os.path.join(CHAT_HISTORIES_DIR, f"chat_history_{self.chat_history_id}.json")
        with open(file_path, 'w', encoding="utf-8") as file:
            json.dump(self.__dict__, file, ensure_ascii=False, indent=2)
    
    def delete(self):
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

    