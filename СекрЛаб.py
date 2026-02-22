#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import customtkinter as ctk
from tkinter import messagebox, simpledialog, filedialog
import math
import random
import re
import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import queue
import time
from collections import Counter
import datetime
import urllib.request
import urllib.error
import socket
import importlib.util
import hashlib

# ==================== ОПЦИОНАЛЬНЫЕ БИБЛИОТЕКИ ====================
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    import matplotlib
    matplotlib.use('TkAgg')
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    MATPLOTLIB_OK = True
except ImportError:
    MATPLOTLIB_OK = False

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.pipeline import make_pipeline
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# ==================== КОНСТАНТЫ ====================
AUTHOR = "Даниил Низов"
VERSION = "44.0"

# ==================== ОПРЕДЕЛЕНИЕ ТИПА УСТРОЙСТВА ====================
def is_mobile():
    try:
        screen_width = ctk.CTk().winfo_screenwidth()
        return screen_width < 800
    except:
        return False

MOBILE = is_mobile()

# ==================== КЛАССЫ БЕЗОПАСНОСТИ ====================
class ConnectionManager:
    def __init__(self):
        self.connected = False
        self.last_check = 0
        self.check_interval = 60

    def check_connection(self, force=False):
        current = time.time()
        if not force and current - self.last_check < self.check_interval:
            return self.connected
        self.last_check = current
        try:
            hosts = ["8.8.8.8", "1.1.1.1"]
            for host in hosts:
                try:
                    socket.create_connection((host, 53), timeout=2)
                    self.connected = True
                    return True
                except:
                    continue
            self.connected = False
            return False
        except:
            self.connected = False
            return False

class SecurityManager:
    DANGEROUS_KEYWORDS = [
        'rm -rf', 'del /', 'format', 'mkfs', 'dd if=', '> /dev/sda',
        'chmod 777', 'chown', 'sudo', 'su ', 'passwd', 'shutdown',
        'reboot', 'init 0', 'kill -9', 'pkill', 'systemctl',
        'удалить систем', 'стереть диск', 'форматировать',
        'стерсть все файлы', 'удалить виндовс', 'удалить windows'
    ]

    @staticmethod
    def is_path_safe(path):
        if not path:
            return False
        path = os.path.abspath(path)
        forbidden = [
            '/etc', '/bin', '/sbin', '/boot', '/dev', '/proc', '/sys',
            '/usr', '/var', '/lib', '/root',
            'C:\\Windows', 'C:\\Program Files', 'C:\\ProgramData',
            'C:\\System Volume Information', 'D:\\', 'E:\\'
        ]
        for f in forbidden:
            if path.startswith(f):
                return False
        if path in ['/', 'C:\\', 'D:\\', 'E:\\']:
            return False
        return True

    @staticmethod
    def contains_dangerous_command(text):
        text_lower = text.lower()
        for kw in SecurityManager.DANGEROUS_KEYWORDS:
            if kw in text_lower:
                return True
        dangerous_imports = ['os.system', 'subprocess.Popen', 'exec(', 'eval(',
                             '__import__', 'open(', 'file(', 'shutil.rmtree',
                             'os.remove', 'os.unlink', 'os.chmod', 'os.kill']
        for imp in dangerous_imports:
            if imp in text:
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
    def atbash(text):
        result = []
        for c in text:
            if c.isalpha():
                if c.islower():
                    result.append(chr(ord('z') - (ord(c) - ord('a'))))
                else:
                    result.append(chr(ord('Z') - (ord(c) - ord('A'))))
            else:
                result.append(c)
        return ''.join(result)

    @staticmethod
    def xor(text, key):
        try:
            key_int = int(key) % 256
            return ''.join(chr(ord(c) ^ key_int) for c in text)
        except:
            return "Ошибка: ключ должен быть числом"

    @staticmethod
    def base64_encode(text):
        return base64.b64encode(text.encode()).decode()

    @staticmethod
    def base64_decode(text):
        try:
            return base64.b64decode(text).decode()
        except:
            return "Ошибка декодирования Base64"

    @staticmethod
    def reverse(text):
        return text[::-1]

    @staticmethod
    def vigenere(text, key, decrypt=False):
        key = key.upper()
        result = []
        key_index = 0
        for c in text:
            if c.isalpha():
                shift = ord(key[key_index % len(key)]) - 65
                if decrypt:
                    shift = -shift
                if c.islower():
                    result.append(chr((ord(c) - 97 + shift) % 26 + 97))
                else:
                    result.append(chr((ord(c) - 65 + shift) % 26 + 65))
                key_index += 1
            else:
                result.append(c)
        return ''.join(result)

# ==================== ПЕСОЧНИЦА ДЛЯ ВИРУСОВ ====================
class SafeSandbox:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="sandbox_")
        self.process = None
        self.running = False
        self.start_time = None
        self.max_duration = 30
        self.max_cpu = 50
        self.max_memory = 200
        self.monitor_thread = None
        self.callback = None
        self.output_queue = queue.Queue()
        self.lock = threading.Lock()

    def cleanup(self):
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass

    def monitor_process(self):
        while self.running and self.process and self.process.poll() is None:
            try:
                if time.time() - self.start_time > self.max_duration:
                    self.stop("Превышено максимальное время выполнения")
                    return
                if PSUTIL_AVAILABLE:
                    p = psutil.Process(self.process.pid)
                    cpu = p.cpu_percent(interval=0.5)
                    if cpu > self.max_cpu:
                        self.stop(f"Превышено использование CPU: {cpu}%")
                        return
                    mem = p.memory_info().rss / 1024 / 1024
                    if mem > self.max_memory:
                        self.stop(f"Превышено использование памяти: {mem:.1f} MB")
                        return
                time.sleep(0.5)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break
            except Exception:
                time.sleep(0.5)

    def stop(self, reason="Остановлено пользователем"):
        with self.lock:
            if self.running and self.process:
                try:
                    self.process.terminate()
                    time.sleep(1)
                    if self.process.poll() is None:
                        self.process.kill()
                except:
                    pass
                self.running = False
                if self.callback:
                    self.callback("stopped", reason)

    def run_script(self, script_path, script_args=None, callback=None):
        if not os.path.exists(script_path):
            if callback:
                callback("error", "Файл скрипта не найден")
            return False
        self.callback = callback
        self.start_time = time.time()

        def target():
            try:
                sandbox_script = os.path.join(self.temp_dir, os.path.basename(script_path))
                shutil.copy2(script_path, sandbox_script)
                env = os.environ.copy()
                env['SANDBOX_DIR'] = self.temp_dir
                env['PYTHONPATH'] = ''
                # Пытаемся запустить процесс
                try:
                    self.process = subprocess.Popen(
                        [sys.executable, sandbox_script] + (script_args or []),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        bufsize=1,
                        env=env,
                        cwd=self.temp_dir
                    )
                except Exception as e:
                    if callback:
                        callback("error", f"Не удалось запустить процесс: {e}\nСкрипт сохранён в {sandbox_script}")
                    return
                self.running = True
                self.monitor_thread = threading.Thread(target=self.monitor_process)
                self.monitor_thread.daemon = True
                self.monitor_thread.start()
                for line in iter(self.process.stdout.readline, ''):
                    if callback:
                        callback("output", line)
                for line in iter(self.process.stderr.readline, ''):
                    if callback:
                        callback("error_output", line)
                self.process.wait()
                with self.lock:
                    if self.running:
                        self.running = False
                        if callback:
                            callback("done", f"Процесс завершён с кодом {self.process.returncode}")
            except Exception as e:
                with self.lock:
                    self.running = False
                if callback:
                    callback("error", str(e))

        threading.Thread(target=target, daemon=True).start()
        return True

# ==================== ЛАБОРАТОРИЯ ВИРУСОВ ====================
class VirusLab:
    SAFE_VIRUS_TEMPLATES = {
        "fork_bomb_demo": {
            "name": "Fork-бомба",
            "description": "Создаёт процессы, ограничен по времени и количеству",
            "warning": "Создаёт новые процессы. Автоматически остановится через 5 секунд.",
            "code": """import os, time, sys
MAX_PROCESSES = 20
START_TIME = time.time()
MAX_DURATION = 5
def create_processes(level=0):
    if level > 3: return
    if time.time() - START_TIME > MAX_DURATION: return
    processes = []
    for i in range(2):
        try:
            pid = os.fork()
            if pid == 0:
                print(f"Дочерний процесс {level}.{i} создан")
                time.sleep(1)
                create_processes(level+1)
                os._exit(0)
            else:
                processes.append(pid)
        except: break
    for pid in processes:
        os.waitpid(pid, 0)
if __name__ == "__main__":
    print("Демонстрация fork-бомбы (безопасная версия)")
    create_processes()
    print("Демо завершено")
"""
        },
        "cpu_burner_demo": {
            "name": "Нагрузка на CPU",
            "description": "Интенсивные вычисления с контролем времени",
            "warning": "Нагружает процессор. Автоматически остановится через 10 секунд.",
            "code": """import math, time, threading
START_TIME = time.time()
MAX_DURATION = 10
RUNNING = True
def cpu_worker(thread_id):
    count = 0
    while RUNNING and time.time() - START_TIME < MAX_DURATION:
        for i in range(100000):
            x = math.sqrt(i) * math.pi
        count += 1
        print(f"Поток {thread_id}: итерация {count}")
        time.sleep(0.1)
if __name__ == "__main__":
    print("Демонстрация нагрузки на CPU")
    threads = [threading.Thread(target=cpu_worker, args=(i,)) for i in range(4)]
    for t in threads:
        t.daemon = True
        t.start()
    try:
        time.sleep(MAX_DURATION + 1)
    except KeyboardInterrupt:
        RUNNING = False
    RUNNING = False
    print("Демо завершено")
"""
        },
        "memory_eater_demo": {
            "name": "Потребление памяти",
            "description": "Постепенное выделение памяти с контролем",
            "warning": "Потребляет память. Автоматически остановится при превышении 100 MB.",
            "code": """import time
START_TIME = time.time()
MAX_DURATION = 15
MAX_MEMORY_MB = 100
data = []
try:
    print("Демонстрация потребления памяти")
    while time.time() - START_TIME < MAX_DURATION:
        data.append(' ' * (1024*1024))
        mem = len(data)
        print(f"Выделено {mem} MB")
        if mem > MAX_MEMORY_MB:
            print("Достигнут лимит памяти")
            break
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    data = None
    print("Демо завершено, память освобождена")
"""
        },
        "file_creator_demo": {
            "name": "Создание файлов",
            "description": "Создаёт временные файлы в изолированной директории",
            "warning": "Файлы создаются только в песочнице и будут удалены.",
            "code": """import os, time
sandbox = os.environ.get('SANDBOX_DIR', '.')
print(f"Работаем в песочнице: {sandbox}")
for i in range(10):
    path = os.path.join(sandbox, f"test_{i}.txt")
    with open(path, 'w') as f:
        f.write(f"Тестовый файл {i}\\n")
    print(f"Создан файл: {path}")
    time.sleep(0.5)
print("Список созданных файлов:")
for f in os.listdir(sandbox):
    if f.startswith('test_'):
        size = os.path.getsize(os.path.join(sandbox, f))
        print(f"  {f} ({size} байт)")
print("Демо завершено")
"""
        },
        "network_scanner_demo": {
            "name": "Сканер портов",
            "description": "Сканирует локальные порты (только localhost)",
            "warning": "Сканирует только localhost. Безопасно для сети.",
            "code": """import socket
def scan_port(host, port):
    try:
        s = socket.socket()
        s.settimeout(0.5)
        result = s.connect_ex((host, port))
        s.close()
        return result == 0
    except: return False
print("Сканирование локальных портов")
target = '127.0.0.1'
open_ports = []
for port in range(1, 1024):
    if scan_port(target, port):
        print(f"Порт {port} открыт")
        open_ports.append(port)
    if port % 100 == 0:
        print(f"Сканировано {port} портов...")
print(f"Открытые порты: {open_ports}")
print("Демо завершено")
"""
        }
    }

    def __init__(self):
        self.active_sandboxes = []

    def get_virus_list(self):
        return [(key, data['name'], data['description']) for key, data in self.SAFE_VIRUS_TEMPLATES.items()]

    def create_virus_script(self, virus_key):
        if virus_key not in self.SAFE_VIRUS_TEMPLATES:
            return None, "Неизвестный тип вируса"
        template = self.SAFE_VIRUS_TEMPLATES[virus_key]
        temp_dir = tempfile.mkdtemp(prefix="virus_lab_")
        script_path = os.path.join(temp_dir, f"{virus_key}.py")
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(template['code'])
        return script_path, template

    def run_virus(self, virus_key, callback=None):
        script_path, template = self.create_virus_script(virus_key)
        if not script_path:
            return None
        sandbox = SafeSandbox()
        def sandbox_callback(event, data):
            if event in ("done", "stopped", "error"):
                if sandbox in self.active_sandboxes:
                    self.active_sandboxes.remove(sandbox)
                sandbox.cleanup()
            if callback:
                callback(event, data)
        success = sandbox.run_script(script_path, callback=sandbox_callback)
        if success:
            self.active_sandboxes.append(sandbox)
            return id(sandbox)
        return None

    def stop_all(self):
        for sandbox in self.active_sandboxes[:]:
            sandbox.stop("Принудительная остановка всех процессов")

# ==================== КЛАСС ДЛЯ ИНТЕРНЕТ-ПОИСКА ====================
class SimpleWebSearch:
    def __init__(self):
        self.session = None
        if REQUESTS_AVAILABLE:
            self.session = requests.Session()
            self.session.headers.update({'User-Agent': 'Mozilla/5.0'})
        else:
            self.session = None

    def search_wikipedia(self, query):
        if not REQUESTS_AVAILABLE:
            return None
        try:
            url = "https://ru.wikipedia.org/w/api.php"
            params = {
                'action': 'query',
                'list': 'search',
                'srsearch': query,
                'format': 'json',
                'srlimit': 2
            }
            resp = self.session.get(url, params=params, timeout=5)
            data = resp.json()
            if data.get('query', {}).get('search'):
                results = []
                for item in data['query']['search']:
                    results.append({
                        'title': item['title'],
                        'snippet': re.sub(r'<[^>]+>', '', item['snippet'])
                    })
                return results
        except:
            pass
        return None

    def search_duckduckgo(self, query):
        if not REQUESTS_AVAILABLE:
            return None
        try:
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': 1,
                'skip_disambig': 1
            }
            resp = self.session.get(url, params=params, timeout=5)
            data = resp.json()
            if data.get('AbstractText'):
                return data['AbstractText']
            elif data.get('Answer'):
                return data['Answer']
        except:
            pass
        return None

# ==================== БАЗА ЗНАНИЙ ====================
class KnowledgeBase:
    def __init__(self, kb_file='knowledge.json'):
        self.kb_file = kb_file
        self.qa_pairs = self.load()
        self.vectorizer = None
        self.vectors = None
        self.model = None
        if SKLEARN_AVAILABLE and len(self.qa_pairs) > 5:
            self.train_model()

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
        if SKLEARN_AVAILABLE:
            self.train_model()

    def train_model(self):
        if not SKLEARN_AVAILABLE or len(self.qa_pairs) == 0:
            return
        questions = [item['question'] for item in self.qa_pairs]
        answers = [item['answer'] for item in self.qa_pairs]
        self.vectorizer = TfidfVectorizer(ngram_range=(1,2), analyzer='word', lowercase=True)
        self.vectors = self.vectorizer.fit_transform(questions)
        self.model = HistGradientBoostingClassifier(max_iter=100, random_state=42)
        self.model.fit(self.vectors, answers)

    def search(self, query):
        if self.vectorizer and self.vectors is not None:
            q_vec = self.vectorizer.transform([query])
            sim = cosine_similarity(q_vec, self.vectors).flatten()
            best_idx = sim.argmax()
            best_score = sim[best_idx]
            if best_score > 0.75:
                return self.qa_pairs[best_idx]['answer']
        # fallback: простое совпадение слов
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
    def __init__(self, root, knowledge_base, virus_lab, progress_callback=None):
        self.root = root
        self.kb = knowledge_base
        self.virus_lab = virus_lab
        self.progress_callback = progress_callback
        self.cipher_lab = CipherLab()
        self.web = SimpleWebSearch()
        self.conn_manager = ConnectionManager()
        self.exam_mode = False
        self.current_exam_task = None

    def _progress(self, msg, val):
        if self.progress_callback:
            self.progress_callback(msg, val)

    # ----- Определение типа запроса -----
    def is_math_query(self, q):
        if self.is_virus_query(q) or self.is_cipher_query(q):
            return False
        return bool(re.search(r'(?:вычисли|посчитай|найди|найти|сколько будет)', q, re.IGNORECASE)) or \
               re.search(r'[0-9+\-*/()\^]', q) is not None or \
               re.search(r'(?:площадь|объем|периметр|гипотенуза|корень|sin|cos|tg|log|ln)', q, re.IGNORECASE) is not None

    def is_equation(self, q):
        return '=' in q and not q.startswith('==')

    def is_cipher_query(self, q):
        patterns = [r'зашифруй', r'расшифруй', r'шифр', r'цезарь', r'xor', r'base64', r'атбаш', r'atbash', r'rot13', r'переверни']
        return any(re.search(p, q, re.IGNORECASE) for p in patterns)

    def is_virus_query(self, q):
        patterns = [
            r'создай вирус', r'сделай вирус', r'вирус',
            r'запусти вирус', r'запустить вирус',
            r'fork[ -]?bomb', r'fork-бомба', r'fork бомба',
            r'cpu[ -]?burner', r'cpu burner', r'процессор',
            r'нагрузка на процессор', r'нагрузить процессор',
            r'memory[ -]?eater', r'потребление памяти', r'память',
            r'file[ -]?creator', r'создание файлов', r'файловый',
            r'network[ -]?scanner', r'scan[ -]?ports', r'сканировать порты',
            r'сетевой скан'
        ]
        return any(re.search(p, q, re.IGNORECASE) for p in patterns)

    def is_file_query(self, q):
        patterns = [r'прочитай файл', r'открой файл', r'покажи файл']
        return any(re.search(p, q, re.IGNORECASE) for p in patterns)

    def is_plot_query(self, q):
        patterns = [r'график', r'построй', r'plot']
        return any(re.search(p, q, re.IGNORECASE) for p in patterns)

    def is_exam_query(self, q):
        patterns = [r'обучи меня', r'дай задачу', r'тренируй']
        return any(re.search(p, q, re.IGNORECASE) for p in patterns)

    # ----- Обработчики -----
    def extract_expression(self, q):
        patterns = [
            r'(?:вычисли|посчитай|найди|найти|сколько будет)[:\s]*([^,.?]+)',
            r'y\s*=\s*([^,.?]+)',
            r'f\(x\)\s*=\s*([^,.?]+)',
            r'([0-9+\-*/\(\)\^]+)',
            r'(?:площадь|объем|периметр|гипотенуза)[:\s]*([^,.?]+)',
        ]
        for pat in patterns:
            m = re.search(pat, q, re.IGNORECASE)
            if m:
                expr = m.group(1).strip()
                expr = expr.rstrip('.')
                return expr
        return None

    def handle_math(self, q):
        if self.is_math_query(q) or self.is_equation(q):
            expr = self.extract_expression(q)
            if expr:
                try:
                    allowed = {k: v for k, v in math.__dict__.items() if not k.startswith('__')}
                    result = eval(expr, {"__builtins__": {}}, allowed)
                    return f"Результат: {result}"
                except Exception as e:
                    return f"Ошибка вычисления: {e}"
        return None

    def handle_cipher(self, q):
        if not self.is_cipher_query(q):
            return None
        ql = q.lower()

        if 'цезарь' in ql:
            match = re.search(r'"([^"]+)"', q)
            if not match:
                return "Укажите текст в кавычках"
            text = match.group(1)
            shift = 3
            shift_match = re.search(r'(\d+)', q)
            if shift_match:
                shift = int(shift_match.group(1))
            if 'расшифруй' in ql:
                result = self.cipher_lab.caesar(text, shift, decrypt=True)
            else:
                result = self.cipher_lab.caesar(text, shift)
            return f"Результат: {result}"

        if 'атбаш' in ql or 'atbash' in ql:
            match = re.search(r'"([^"]+)"', q)
            if not match:
                return "Укажите текст в кавычках"
            result = self.cipher_lab.atbash(match.group(1))
            return f"Результат: {result}"

        if 'xor' in ql:
            match = re.search(r'"([^"]+)"', q)
            if not match:
                return "Укажите текст в кавычках"
            key_match = re.search(r'(\d+)', q)
            if not key_match:
                return "Укажите ключ (число)"
            result = self.cipher_lab.xor(match.group(1), key_match.group(1))
            return f"Результат: {result}"

        if 'base64' in ql:
            match = re.search(r'"([^"]+)"', q)
            if not match:
                return "Укажите текст в кавычках"
            if 'закодируй' in ql or 'encode' in ql:
                result = self.cipher_lab.base64_encode(match.group(1))
                return f"Результат: {result}"
            else:
                result = self.cipher_lab.base64_decode(match.group(1))
                return f"Результат: {result}"

        if 'переверни' in ql or 'reverse' in ql:
            match = re.search(r'"([^"]+)"', q)
            if not match:
                return "Укажите текст в кавычках"
            result = self.cipher_lab.reverse(match.group(1))
            return f"Результат: {result}"

        return "Неизвестная операция шифрования"

    def handle_virus(self, q):
        if not self.is_virus_query(q):
            return None
        ql = q.lower()

        if 'список' in ql:
            viruses = self.virus_lab.get_virus_list()
            result = "📋 Доступные вирусы:\n\n"
            for key, name, desc in viruses:
                result += f"• {name}: {desc}\n  Команда: создай вирус {key.replace('_', ' ')}\n\n"
            return result

        virus_key = None
        if 'fork' in ql or 'бомб' in ql:
            virus_key = 'fork_bomb_demo'
        elif 'cpu' in ql or 'процессор' in ql or 'нагрузк' in ql:
            virus_key = 'cpu_burner_demo'
        elif 'memory' in ql or 'памят' in ql or 'eater' in ql:
            virus_key = 'memory_eater_demo'
        elif 'file' in ql or 'файл' in ql or 'creator' in ql:
            virus_key = 'file_creator_demo'
        elif 'network' in ql or 'сет' in ql or 'порт' in ql or 'scan' in ql:
            virus_key = 'network_scanner_demo'
        else:
            # fallback to template names
            for key in self.virus_lab.SAFE_VIRUS_TEMPLATES:
                if key.replace('_', ' ') in ql or self.virus_lab.SAFE_VIRUS_TEMPLATES[key]['name'].lower() in ql:
                    virus_key = key
                    break

        if virus_key:
            def callback(event, data):
                if event == "output":
                    self.root.after(0, lambda: self.root.answer_text.insert("end", f"[ВИРУС] {data}"))
                elif event == "error_output":
                    self.root.after(0, lambda: self.root.answer_text.insert("end", f"[ОШИБКА] {data}"))
                elif event == "done":
                    self.root.after(0, lambda: messagebox.showinfo("Вирус завершён", data))
                elif event == "stopped":
                    self.root.after(0, lambda: messagebox.showwarning("Вирус остановлен", data))
                elif event == "error":
                    self.root.after(0, lambda: messagebox.showerror("Ошибка", data))

            virus_id = self.virus_lab.run_virus(virus_key, callback)
            if virus_id:
                return f"✅ Вирус '{self.virus_lab.SAFE_VIRUS_TEMPLATES[virus_key]['name']}' запущен. Следите за выводом."
            else:
                return "❌ Не удалось запустить вирус. Возможно, на вашей платформе это не поддерживается. Скрипт сохранён во временной папке."

        return "Не удалось определить тип вируса. Используйте 'список вирусов' для просмотра доступных."

    def handle_file(self, q):
        if not self.is_file_query(q):
            return None
        match = re.search(r'"([^"]+)"', q)
        if not match:
            return "Укажите путь в кавычках"
        path = match.group(1)
        if not SecurityManager.is_path_safe(path):
            return "⚠️ Доступ к файлу запрещён по соображениям безопасности"
        if not os.path.exists(path):
            return f"Файл {path} не найден"
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read(500)
            if len(content) == 500:
                content += "..."
            return f"Содержимое {path}:\n{content}"
        except Exception as e:
            return f"Ошибка чтения: {e}"

    def handle_plot(self, q):
        if not self.is_plot_query(q) or not MATPLOTLIB_OK:
            return None
        match = re.search(r'(?:график|построй)[:\s]*([^,.?]+)', q, re.IGNORECASE)
        if not match:
            return "Не удалось распознать функцию"
        func = match.group(1).strip().replace('^', '**')
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            x = np.linspace(-10, 10, 200)
            y = eval(func, {"__builtins__": {}}, {"x": x, "np": np, "sin": np.sin, "cos": np.cos,
                                                   "tan": np.tan, "exp": np.exp, "log": np.log,
                                                   "sqrt": np.sqrt, "pi": np.pi})
            plt.figure()
            plt.plot(x, y)
            plt.title(f"График: {func}")
            plt.grid(True)
            plt.show()
            return "График построен"
        except Exception as e:
            return f"Ошибка построения графика: {e}"

    def handle_exam(self, q):
        if not self.is_exam_query(q):
            return None

        # Генерируем случайный вопрос из базы знаний (для обучения)
        if self.kb.qa_pairs:
            item = random.choice(self.kb.qa_pairs)
            self.current_exam_task = item
            self.exam_mode = True
            return f"📚 Обучающий вопрос:\n{item['question']}\n\nВведите ваш ответ:"
        else:
            return "База знаний пуста. Сначала добавьте вопросы через обычные запросы."

    def handle_exam_answer(self, answer):
        if not self.exam_mode or not self.current_exam_task:
            return None
        task = self.current_exam_task
        correct = task['answer']
        if answer.strip().lower() == correct.lower():
            self.exam_mode = False
            self.current_exam_task = None
            return "✅ Верно! Можете попросить ещё задачу."
        else:
            self.exam_mode = False
            self.current_exam_task = None
            return f"❌ Неверно. Правильный ответ: {correct}"

    def handle_internet(self, q):
        if not REQUESTS_AVAILABLE:
            return "Библиотека requests не установлена. Интернет-поиск недоступен."
        if not self.conn_manager.check_connection():
            return None
        self._progress("Поиск в Wikipedia...", 30)
        wiki = self.web.search_wikipedia(q)
        if wiki:
            result = "📚 Найдено в Wikipedia:\n"
            for item in wiki:
                result += f"• {item['title']}: {item['snippet']}\n"
            return result
        ddg = self.web.search_duckduckgo(q)
        if ddg:
            return f"🔍 DuckDuckGo: {ddg}"
        return None

    def ask(self, question):
        q = question.strip()
        if not q:
            return "Введите запрос."

        if SecurityManager.contains_dangerous_command(q):
            return "⚠️ Запрос содержит потенциально опасные команды и был заблокирован."

        # Если в режиме экзамена, обрабатываем ответ
        if self.exam_mode and self.current_exam_task:
            return self.handle_exam_answer(q)

        # Проверяем специальные команды
        if self.is_virus_query(q):
            virus_res = self.handle_virus(q)
            if virus_res:
                return virus_res

        if self.is_cipher_query(q):
            cipher_res = self.handle_cipher(q)
            if cipher_res:
                return cipher_res

        if self.is_exam_query(q):
            exam_res = self.handle_exam(q)
            if exam_res:
                return exam_res

        # Математика
        math_res = self.handle_math(q)
        if math_res:
            return math_res

        # Файлы
        file_res = self.handle_file(q)
        if file_res:
            return file_res

        # Графики
        plot_res = self.handle_plot(q)
        if plot_res:
            return plot_res

        # Интернет
        internet_res = self.handle_internet(q)
        if internet_res:
            return internet_res

        # База знаний
        kb_res = self.kb.search(q)
        if kb_res:
            return f"📖 Из базы знаний: {kb_res}"

        # Обучение
        ans = simpledialog.askstring("Обучение", f"Не знаю ответа. Введите правильный ответ для обучения:\n\n{q}", parent=self.root)
        if ans:
            self.kb.add(q, ans)
            return f"✅ Спасибо! Ответ сохранён: {ans}"

        return "🤔 Не знаю ответа. Попробуйте переформулировать."

# ==================== ФАЙЛОВЫЙ МЕНЕДЖЕР (исправленный для мобильных) ====================
class FileManagerWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Файловый менеджер")
        self.geometry("600x500")
        self.current_path = os.path.expanduser("~")

        # Верхняя панель с путём
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(fill=tk.X, padx=5, pady=5)

        self.path_label = ctk.CTkLabel(top_frame, text=self.current_path, anchor="w")
        self.path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.up_btn = ctk.CTkButton(top_frame, text="⬆ Наверх", width=80, command=self.go_up)
        self.up_btn.pack(side=tk.RIGHT, padx=5)

        # Список файлов (используем CTkScrollableFrame для лучшей совместимости)
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.file_buttons = []  # для хранения кнопок

        self.refresh()

    def refresh(self):
        # Очищаем старые кнопки
        for btn in self.file_buttons:
            btn.destroy()
        self.file_buttons.clear()

        try:
            items = os.listdir(self.current_path)
            for name in sorted(items):
                full = os.path.join(self.current_path, name)
                if os.path.isdir(full):
                    text = f"📁 {name}"
                else:
                    size = os.path.getsize(full)
                    text = f"📄 {name} ({size} байт)"

                btn = ctk.CTkButton(
                    self.scroll_frame,
                    text=text,
                    anchor="w",
                    command=lambda f=full, d=os.path.isdir(full): self.on_item_click(f, d)
                )
                btn.pack(fill=tk.X, padx=2, pady=1)
                self.file_buttons.append(btn)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

        self.path_label.configure(text=self.current_path)

    def go_up(self):
        parent = os.path.dirname(self.current_path)
        if parent and parent != self.current_path:
            self.current_path = parent
            self.refresh()

    def on_item_click(self, full, is_dir):
        if is_dir:
            self.current_path = full
            self.refresh()
        else:
            try:
                with open(full, 'r', encoding='utf-8') as f:
                    content = f.read(500)
                messagebox.showinfo(os.path.basename(full), content)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось прочитать файл: {e}")

# ==================== НОВЫЙ КЛАСС ПРИЛОЖЕНИЯ (CustomTkinter) ====================
class ModernCalculatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Настройки окна
        self.title("🚀 Нейро-калькулятор • Лаборатория безопасности")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}")
        self.minsize(350, 500)

        # Настройка сетки
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Масштабирование шрифтов: на мобильных увеличиваем
        self.font_scale = 1.5 if MOBILE else 1.0

        # Компоненты
        self.conn_manager = ConnectionManager()
        self.knowledge_base = KnowledgeBase()
        self.virus_lab = VirusLab()
        self.assistant = SmartAssistant(self, self.knowledge_base, self.virus_lab, self.update_progress)
        self.assistant.root = self  # для доступа к answer_text

        self.create_ui()
        self.update_internet_status()
        self.show_welcome_message()

    def get_font(self, size, bold=False):
        """Возвращает шрифт заданного размера с учётом масштаба."""
        actual_size = int(size * self.font_scale)
        weight = "bold" if bold else "normal"
        return ctk.CTkFont(size=actual_size, weight=weight)

    def create_ui(self):
        # Верхняя панель
        top_frame = ctk.CTkFrame(self)
        top_frame.grid(row=0, column=0, padx=10, pady=(10,5), sticky="ew")
        top_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            top_frame,
            text="🔐 Лаборатория безопасности",
            font=self.get_font(22, bold=True)
        )
        title.pack(pady=5)

        self.internet_label = ctk.CTkLabel(
            top_frame,
            text="🔴 Автономный режим",
            font=self.get_font(14)
        )
        self.internet_label.pack()

        # Поле ввода
        input_frame = ctk.CTkFrame(self)
        input_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        input_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            input_frame,
            text="👤 Запрос:",
            font=self.get_font(16, bold=True)
        ).grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.question_entry = ctk.CTkTextbox(
            input_frame,
            height=100,
            font=self.get_font(16)
        )
        self.question_entry.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        send_btn = ctk.CTkButton(
            input_frame,
            text="🚀 Отправить",
            command=self.ask,
            font=self.get_font(16, bold=True),
            height=50
        )
        send_btn.grid(row=2, column=1, padx=5, pady=5, sticky="e")

        # Область ответа
        answer_frame = ctk.CTkFrame(self)
        answer_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        answer_frame.grid_columnconfigure(0, weight=1)
        answer_frame.grid_rowconfigure(1, weight=1)

        header_frame = ctk.CTkFrame(answer_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=5, pady=2, sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header_frame,
            text="🤖 Ответ:",
            font=self.get_font(16, bold=True)
        ).grid(row=0, column=0, padx=5, pady=2, sticky="w")

        ctk.CTkLabel(
            header_frame,
            text="(сообщения AI выделены)",
            font=self.get_font(12)
        ).grid(row=0, column=1, padx=5, pady=2, sticky="e")

        self.answer_text = ctk.CTkTextbox(
            answer_frame,
            font=self.get_font(16),
            wrap="word"
        )
        self.answer_text.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        # Кнопки быстрого доступа
        btn_frame = ctk.CTkFrame(self)
        btn_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        btn_frame.grid_columnconfigure((0,1,2,3,4), weight=1)

        buttons = [
            ("🦠 Вирусы", self.show_virus_list, "#4cc9f0"),
            ("⏹️ Стоп", self.stop_all_viruses, "#f94144"),
            ("🔐 Шифры", self.show_ciphers, "#f8961e"),
            ("📁 Файлы", self.open_file_manager, "#4361ee"),
            ("🧹 Очистить", self.clear_screen, "#4895ef"),
        ]

        for i, (text, cmd, color) in enumerate(buttons):
            btn = ctk.CTkButton(
                btn_frame,
                text=text,
                command=cmd,
                font=self.get_font(14, bold=True),
                height=50,
                fg_color=color,
                hover_color=self._adjust_color(color, -20)
            )
            btn.grid(row=0, column=i, padx=2, pady=5, sticky="ew")

        # Строка состояния
        self.status = ctk.CTkLabel(
            self,
            text="Готов",
            font=self.get_font(12),
            anchor="w"
        )
        self.status.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

        self.bind('<Return>', lambda e: self.ask())

    def _adjust_color(self, hex_color, amount):
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0,2,4))
        new_rgb = tuple(max(0, min(255, c+amount)) for c in rgb)
        return f"#{new_rgb[0]:02x}{new_rgb[1]:02x}{new_rgb[2]:02x}"

    def show_welcome_message(self):
        welcome = """
🤖 **Нейро-помощник** готов к работе!

Я могу:
• Вычислять математику
• Шифровать текст
• Создавать демо-вирусы
• Читать файлы
• Строить графики
• Искать в интернете
• Обучаться на ваших вопросах

👉 Просто напишите запрос!"""
        self.answer_text.insert("0.0", welcome)

    def update_internet_status(self):
        if self.conn_manager.check_connection():
            self.internet_label.configure(text="🟢 Интернет подключён", text_color="green")
        else:
            self.internet_label.configure(text="🔴 Автономный режим", text_color="red")
        self.after(10000, self.update_internet_status)

    def update_progress(self, message, value):
        self.status.configure(text=message)

    def ask(self):
        q = self.question_entry.get("0.0", "end").strip()
        if not q:
            messagebox.showinfo("Информация", "Введите запрос.")
            return

        self.answer_text.insert("end", f"\n\n👤 Вы: {q}\n")
        answer = self.assistant.ask(q)
        self.answer_text.insert("end", f"🤖 {answer}\n")
        self.answer_text.see("end")
        self.question_entry.delete("0.0", "end")

    def show_virus_list(self):
        viruses = self.virus_lab.get_virus_list()
        result = "🦠 Доступные вирусы:\n\n"
        for key, name, desc in viruses:
            result += f"• {name}: {desc}\n  Команда: создай вирус {key.replace('_', ' ')}\n\n"
        self.answer_text.insert("end", f"\n\n{result}")
        self.answer_text.see("end")

    def stop_all_viruses(self):
        self.virus_lab.stop_all()
        self.answer_text.insert("end", f"\n\n⏹️ Все активные процессы остановлены.\n")
        self.answer_text.see("end")

    def show_ciphers(self):
        text = """
🔐 Доступные шифры:
• Цезарь: зашифруй 'текст' цезарем N
• Атбаш: зашифруй 'текст' атбаш
• XOR: зашифруй 'текст' xor 42
• Base64: закодируй 'текст' base64
• Reverse: переверни 'текст'

Примеры:
  зашифруй 'hello' цезарем 3
  расшифруй 'khoor' цезарем 3
  закодируй 'текст' base64
  переверни 'привет'"""
        self.answer_text.insert("end", f"\n\n{text}\n")
        self.answer_text.see("end")

    def open_file_manager(self):
        FileManagerWindow(self)

    def clear_screen(self):
        self.answer_text.delete("0.0", "end")
        self.show_welcome_message()
self.update_idletasks()
print(f"Window geometry: {self.winfo_width()}x{self.winfo_height()}")
print(f"Canvas width: {self.canvas.winfo_width()}")
print(f"Scrollable frame width: {self.scrollable.winfo_width()}")

# ==================== ЗАПУСК ====================
if __name__ == "__main__":
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")
    app = ModernCalculatorApp()
    app.mainloop()