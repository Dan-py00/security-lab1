import flet as ft
import math
import random
import re
import base64
import json
import os
import threading
import subprocess
import tempfile
import time
import requests
from bs4 import BeautifulSoup

# ==================== КОНСТАНТЫ ====================
AUTHOR = "Даниил Низов"
VERSION = "45.0"

# ==================== КЛАССЫ БЕЗОПАСНОСТИ ====================
class SecurityManager:
    DANGEROUS_KEYWORDS = [
        'rm -rf', 'del /', 'format', 'mkfs', 'dd if=', '> /dev/sda',
        'chmod 777', 'chown', 'sudo', 'su ', 'passwd', 'shutdown',
        'reboot', 'init 0', 'kill -9', 'pkill', 'systemctl',
        'удалить систем', 'стереть диск', 'форматировать',
        'стерсть все файлы', 'удалить виндовс', 'удалить windows'
    ]

    @staticmethod
    def contains_dangerous_command(text):
        text_lower = text.lower()
        for kw in SecurityManager.DANGEROUS_KEYWORDS:
            if kw in text_lower:
                return True
        return False

# ==================== КЛАССЫ ШИФРОВ ====================
class CipherLab:
    @staticmethod
    def caesar(text, shift, decrypt=False):
        if decrypt:
            shift = -shift
        result = []
        for c in text:
            if c.isalpha():
                if c.islower():
                    result.append(chr((ord(c) - 97 + shift) % 26 + 97))
                else:
                    result.append(chr((ord(c) - 65 + shift) % 26 + 65))
            else:
                result.append(c)
        return ''.join(result)

    @staticmethod
    def base64_encode(text):
        return base64.b64encode(text.encode()).decode()

    @staticmethod
    def base64_decode(text):
        try:
            return base64.b64decode(text).decode()
        except:
            return "Ошибка декодирования Base64"

# ==================== КЛИЕНТ ФИПИ ====================
class FIPIClient:
    def __init__(self):
        self.base_url = "https://ege.fipi.ru/bank/"
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})
        self.cache = {}
    
    def fetch_task(self):
        try:
            time.sleep(1)
            tasks = [
                {"question": "Решите уравнение x² - 5x + 6 = 0", "answer": "x₁=2, x₂=3"},
                {"question": "Найдите значение выражения sin²α + cos²α", "answer": "1"},
                {"question": "Вычислите log₂ 32", "answer": "5"},
            ]
            return random.choice(tasks)
        except:
            return {"question": "Тестовая задача", "answer": "42"}

# ==================== БАЗА ЗНАНИЙ ====================
class KnowledgeBase:
    def __init__(self, kb_file='knowledge.json'):
        self.kb_file = kb_file
        self.qa_pairs = self.load()
    
    def load(self):
        if os.path.exists(self.kb_file):
            try:
                with open(self.kb_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save(self):
        with open(self.kb_file, 'w', encoding='utf-8') as f:
            json.dump(self.qa_pairs, f, ensure_ascii=False, indent=2)
    
    def add(self, question, answer):
        self.qa_pairs.append({"question": question, "answer": answer})
        self.save()
    
    def search(self, query):
        query_lower = query.lower()
        best_score = 0
        best_item = None
        for item in self.qa_pairs:
            q_lower = item['question'].lower()
            words = set(re.findall(r'\w+', query_lower))
            q_words = set(re.findall(r'\w+', q_lower))
            if words and q_words:
                score = len(words & q_words) / max(len(words), len(q_words))
                if score > best_score and score > 0.5:
                    best_score = score
                    best_item = item
        if best_item:
            return best_item['answer']
        return None

# ==================== ОСНОВНОЙ ПОМОЩНИК ====================
class SmartAssistant:
    def __init__(self):
        self.kb = KnowledgeBase()
        self.cipher = CipherLab()
        self.fipi = FIPIClient()
        self.exam_mode = False
        self.current_task = None
    
    def process_query(self, q):
        q = q.strip()
        if not q:
            return "Введите запрос."
        
        if SecurityManager.contains_dangerous_command(q):
            return "⚠️ Запрос содержит потенциально опасные команды и был заблокирован."
        
        # Математика
        if re.search(r'(?:вычисли|посчитай|сколько будет)', q, re.IGNORECASE):
            try:
                allowed = {k: v for k, v in math.__dict__.items() if not k.startswith('__')}
                expr = re.sub(r'[^0-9+\-*/()\^\.\s]', '', q)
                result = eval(expr, {"__builtins__": {}}, allowed)
                return f"Результат: {result}"
            except:
                pass
        
        # Шифры
        if 'цезарь' in q.lower():
            match = re.search(r'"([^"]+)"', q)
            if match:
                text = match.group(1)
                shift = 3
                shift_match = re.search(r'(\d+)', q)
                if shift_match:
                    shift = int(shift_match.group(1))
                if 'расшифруй' in q.lower():
                    return self.cipher.caesar(text, shift, decrypt=True)
                return self.cipher.caesar(text, shift)
        
        if 'base64' in q.lower():
            match = re.search(r'"([^"]+)"', q)
            if match:
                if 'закодируй' in q.lower():
                    return self.cipher.base64_encode(match.group(1))
                return self.cipher.base64_decode(match.group(1))
        
        # ФИПИ задачи
        if any(word in q.lower() for word in ['фопи', 'fipi', 'фипи', 'задача огэ', 'задача егэ']):
            task = self.fipi.fetch_task()
            self.exam_mode = True
            self.current_task = task
            return f"📚 Задача:\n{task['question']}\n\nВведите ваш ответ:"
        
        # Ответ на задачу
        if self.exam_mode and self.current_task:
            self.exam_mode = False
            if q.strip().lower() == self.current_task['answer'].lower():
                return "✅ Верно!"
            else:
                return f"❌ Неверно. Правильный ответ: {self.current_task['answer']}"
        
        # База знаний
        kb_res = self.kb.search(q)
        if kb_res:
            return f"📖 Из базы знаний: {kb_res}"
        
        return "🤔 Не знаю ответа. Попробуйте переформулировать."

# ==================== ОСНОВНОЕ ПРИЛОЖЕНИЕ ====================
def main(page: ft.Page):
    page.title = "🔐 Нейро-калькулятор"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    
    assistant = SmartAssistant()
    
    question_input = ft.TextField(
        hint_text="Введите ваш запрос...",
        multiline=True,
        min_lines=3,
        max_lines=5,
        border_color=ft.Colors.BLUE_400,
    )
    
    answer_output = ft.Container(
        content=ft.Column([
            ft.Text("🤖 Ответ появится здесь...", size=16, selectable=True)
        ]),
        padding=15,
        bgcolor=ft.Colors.GREY_100,
        border_radius=10,
        expand=True,
    )
    
    def on_submit(e):
        q = question_input.value
        if not q:
            return
        
        answer_output.content.controls.append(
            ft.Text(f"👤 Вы: {q}", size=14, weight=ft.FontWeight.BOLD)
        )
        
        answer = assistant.process_query(q)
        answer_output.content.controls.append(
            ft.Text(f"🤖 {answer}", size=14, selectable=True)
        )
        
        answer_output.content.controls.append(ft.Divider(height=10))
        page.update()
        question_input.value = ""
        page.update()
    
    page.add(
        ft.Column([
            ft.Text("🔐 Лаборатория безопасности", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            question_input,
            ft.ElevatedButton(
                "🚀 Отправить",
                on_click=on_submit,
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.BLUE_600,
                    padding=20,
                )
            ),
            ft.Container(height=10),
            ft.Text("📝 История:", size=16, weight=ft.FontWeight.BOLD),
            answer_output,
        ], expand=True)
    )

if __name__ == "__main__":
    ft.app(target=main)