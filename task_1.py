import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import psutil
import json
import os
import socket
import threading
import xml.etree.ElementTree as ET


class PrilozheniePrakticheskoy:
    def __init__(self, koren):
        self.koren = koren
        self.koren.title("Практическая работа 2.2")
        self.koren.geometry("850x650")

        self.vkladki = ttk.Notebook(self.koren)
        self.vkladki.pack(expand=True, fill='both')

        self.vkladka_sayty = ttk.Frame(self.vkladki)
        self.vkladka_monitor = ttk.Frame(self.vkladki)
        self.vkladka_valyuty = ttk.Frame(self.vkladki)
        self.vkladka_github = ttk.Frame(self.vkladki)
        self.vkladka_tcp = ttk.Frame(self.vkladki)

        self.vkladki.add(self.vkladka_sayty, text="1. Сайты")
        self.vkladki.add(self.vkladka_monitor, text="2. Монитор")
        self.vkladki.add(self.vkladka_valyuty, text="3. Валюты")
        self.vkladki.add(self.vkladka_github, text="4. GitHub")
        self.vkladki.add(self.vkladka_tcp, text="5. TCP Сервер/Клиент")

        self.nastroit_vkladku_sayty()
        self.nastroit_vkladku_monitor()
        self.nastroit_vkladku_valyuty()
        self.nastroit_vkladku_github()
        self.nastroit_vkladku_tcp()

    def nastroit_vkladku_sayty(self):
        self.knopka_proverit_sayty = tk.Button(self.vkladka_sayty, text="Проверить доступность сайтов",
                                               command=self.zapustit_proverku_saytov, font=("Arial", 12))
        self.knopka_proverit_sayty.pack(pady=15)
        self.tekst_sayty = scrolledtext.ScrolledText(self.vkladka_sayty, width=90, height=30, font=("Consolas", 10))
        self.tekst_sayty.pack(padx=10, pady=5)

    def zapustit_proverku_saytov(self):
        self.knopka_proverit_sayty.config(state=tk.DISABLED)
        self.tekst_sayty.delete(1.0, tk.END)
        threading.Thread(target=self.potok_proverki_saytov, daemon=True).start()

    def potok_proverki_saytov(self):
        spisok_saytov = [
            "https://github.com/",
            "https://www.binance.com/en",
            "https://tomtit.tomsk.ru/",
            "https://jsonplaceholder.typicode.com/",
            "https://moodle.tomtit-tomsk.ru/"
        ]
        zagolovki = {"User-Agent": "Mozilla/5.0"}

        for sayt in spisok_saytov:
            try:
                otvet = requests.get(sayt, headers=zagolovki, timeout=5)
                kod = otvet.status_code
                if kod == 200:
                    status = "доступен"
                elif kod == 403:
                    status = "вход запрещен"
                elif kod == 404:
                    status = "не найден"
                elif kod >= 500:
                    status = "не доступен"
                else:
                    status = "неизвестный статус"
                rezultat = f"{sayt} – {status} – {kod}\n"
            except requests.exceptions.RequestException:
                rezultat = f"{sayt} – не доступен – ошибка соединения или таймаут\n"

            self.koren.after(0, lambda r=rezultat: self.tekst_sayty.insert(tk.END, r))

        self.koren.after(0, lambda: self.knopka_proverit_sayty.config(state=tk.NORMAL))

    def nastroit_vkladku_monitor(self):
        self.monitor_id = None

        freym_metok = tk.Frame(self.vkladka_monitor)
        freym_metok.pack(pady=40)

        self.metka_cpu = tk.Label(freym_metok, text="Загрузка CPU: -- %", font=("Arial", 16))
        self.metka_cpu.pack(pady=10)
        self.metka_ozu = tk.Label(freym_metok, text="Использовано ОЗУ: -- ГБ (-- %)", font=("Arial", 16))
        self.metka_ozu.pack(pady=10)
        self.metka_disk = tk.Label(freym_metok, text="Загруженность диска: -- %", font=("Arial", 16))
        self.metka_disk.pack(pady=10)

        freym_knopok = tk.Frame(self.vkladka_monitor)
        freym_knopok.pack(pady=20)

        self.knopka_start_monitor = tk.Button(freym_knopok, text="Начать мониторинг", command=self.start_monitor,
                                              font=("Arial", 12))
        self.knopka_start_monitor.grid(row=0, column=0, padx=10)
        self.knopka_stop_monitor = tk.Button(freym_knopok, text="Остановить", command=self.stop_monitor,
                                             font=("Arial", 12), state=tk.DISABLED)
        self.knopka_stop_monitor.grid(row=0, column=1, padx=10)

    def start_monitor(self):
        self.knopka_start_monitor.config(state=tk.DISABLED)
        self.knopka_stop_monitor.config(state=tk.NORMAL)
        self.obnovit_dannye_monitora()

    def stop_monitor(self):
        if self.monitor_id:
            self.koren.after_cancel(self.monitor_id)
            self.monitor_id = None
        self.knopka_start_monitor.config(state=tk.NORMAL)
        self.knopka_stop_monitor.config(state=tk.DISABLED)
        self.metka_cpu.config(text="Загрузка CPU: -- %")
        self.metka_ozu.config(text="Использовано ОЗУ: -- ГБ (-- %)")
        self.metka_disk.config(text="Загруженность диска: -- %")

    def obnovit_dannye_monitora(self):
        try:
            zagruzka_cpu = psutil.cpu_percent(interval=0)
            ozu = psutil.virtual_memory()
            ispolzovana_ozu_gb = ozu.used / (1024 ** 3)
            koren_diska = psutil.disk_partitions()[0].mountpoint
            disk = psutil.disk_usage(koren_diska)

            self.metka_cpu.config(text=f"Загрузка CPU: {zagruzka_cpu}%")
            self.metka_ozu.config(text=f"Использовано ОЗУ: {ispolzovana_ozu_gb:.2f} ГБ ({ozu.percent}%)")
            self.metka_disk.config(text=f"Загруженность диска: {disk.percent}%")
        except Exception:
            self.stop_monitor()
            messagebox.showerror("Ошибка", "Не удалось получить данные системы.")
            return

        self.monitor_id = self.koren.after(2000, self.obnovit_dannye_monitora)

    def nastroit_vkladku_valyuty(self):
        self.fayl_sohraneniya = 'save.json'
        self.gruppy_valyut = {}
        self.zagruzit_gruppy_valyut()

        freym_upravleniya = tk.Frame(self.vkladka_valyuty)
        freym_upravleniya.pack(pady=10)

        tk.Label(freym_upravleniya, text="Ввод (код валюты или название группы):").grid(row=0, column=0, columnspan=2,
                                                                                        pady=5)
        self.pole_valyuty = tk.Entry(freym_upravleniya, width=40, font=("Arial", 12))
        self.pole_valyuty.grid(row=1, column=0, columnspan=2, pady=5)

        tk.Button(freym_upravleniya, text="Все курсы", command=self.pokazat_vse_valyuty, width=20).grid(row=2, column=0,
                                                                                                        padx=5, pady=5)
        tk.Button(freym_upravleniya, text="Курс по коду", command=self.pokazat_valyutu_po_kodu, width=20).grid(row=2,
                                                                                                               column=1,
                                                                                                               padx=5,
                                                                                                               pady=5)
        tk.Button(freym_upravleniya, text="Создать группу", command=self.sozdat_gruppu_valyut, width=20).grid(row=3,
                                                                                                              column=0,
                                                                                                              padx=5,
                                                                                                              pady=5)
        tk.Button(freym_upravleniya, text="Мои группы", command=self.pokazat_gruppy_valyut, width=20).grid(row=3,
                                                                                                           column=1,
                                                                                                           padx=5,
                                                                                                           pady=5)

        tk.Label(freym_upravleniya, text="Формат для добавления/удаления: ИмяГруппы,КодВалюты").grid(row=4, column=0,
                                                                                                     columnspan=2,
                                                                                                     pady=5)
        tk.Button(freym_upravleniya, text="Добавить в группу", command=self.dobavit_v_gruppu, width=20).grid(row=5,
                                                                                                             column=0,
                                                                                                             padx=5,
                                                                                                             pady=5)
        tk.Button(freym_upravleniya, text="Удалить из группы", command=self.udalit_iz_gruppy, width=20).grid(row=5,
                                                                                                             column=1,
                                                                                                             padx=5,
                                                                                                             pady=5)

        self.tekst_valyuty = scrolledtext.ScrolledText(self.vkladka_valyuty, width=90, height=18, font=("Consolas", 10))
        self.tekst_valyuty.pack(padx=10, pady=5)

    def zagruzit_gruppy_valyut(self):
        try:
            with open(self.fayl_sohraneniya, 'r', encoding='utf-8') as fayl:
                self.gruppy_valyut = json.load(fayl)
        except Exception:
            self.gruppy_valyut = {}

    def sohranit_gruppy_valyut(self):
        try:
            with open(self.fayl_sohraneniya, 'w', encoding='utf-8') as fayl:
                json.dump(self.gruppy_valyut, fayl, ensure_ascii=False, indent=4)
        except Exception as oshibka:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {oshibka}")

    def poluchit_dannye_cbr(self):
        try:
            otvet = requests.get("https://www.cbr-xml-daily.ru/daily_json.js", timeout=5)
            if otvet.status_code == 200:
                return otvet.json()['Valute']
        except Exception:
            return None
        return None

    def vivod_valyut(self, tekst):
        self.tekst_valyuty.delete(1.0, tk.END)
        self.tekst_valyuty.insert(tk.END, tekst)

    def pokazat_vse_valyuty(self):
        dannie = self.poluchit_dannye_cbr()
        if dannie:
            rezultat = "Текущие курсы валют:\n"
            for kod, info in dannie.items():
                rezultat += f"{kod} ({info['Name']}): {info['Value']} руб.\n"
            self.vivod_valyut(rezultat)
        else:
            self.vivod_valyut("Ошибка при получении данных от сервера ЦБ.")

    def pokazat_valyutu_po_kodu(self):
        kod_vvod = self.pole_valyuty.get().strip().upper()
        if not kod_vvod:
            messagebox.showwarning("Внимание", "Введите код валюты.")
            return
        dannie = self.poluchit_dannye_cbr()
        if dannie and kod_vvod in dannie:
            info = dannie[kod_vvod]
            self.vivod_valyut(f"Курс {kod_vvod} ({info['Name']}): {info['Value']} руб.\n")
        else:
            self.vivod_valyut("Валюта не найдена или ошибка сети.")

    def sozdat_gruppu_valyut(self):
        nazvanie = self.pole_valyuty.get().strip()
        if not nazvanie:
            messagebox.showwarning("Внимание", "Введите название группы.")
            return
        if nazvanie in self.gruppy_valyut:
            self.vivod_valyut("Группа с таким названием уже существует.")
        else:
            self.gruppy_valyut[nazvanie] = []
            self.sohranit_gruppy_valyut()
            self.vivod_valyut(f"Группа '{nazvanie}' успешно создана.")
            self.pole_valyuty.delete(0, tk.END)

    def pokazat_gruppy_valyut(self):
        if not self.gruppy_valyut:
            self.vivod_valyut("У вас пока нет сохраненных групп.")
            return
        dannie = self.poluchit_dannye_cbr()
        rezultat = "Ваши группы:\n"
        for nazvanie, spisok_kodov in self.gruppy_valyut.items():
            rezultat += f"\nГруппа: {nazvanie}\n"
            if not spisok_kodov:
                rezultat += "  (пусто)\n"
            else:
                for kod in spisok_kodov:
                    if dannie and kod in dannie:
                        rezultat += f"  {kod}: {dannie[kod]['Value']} руб.\n"
                    else:
                        rezultat += f"  {kod}: нет данных\n"
        self.vivod_valyut(rezultat)

    def dobavit_v_gruppu(self):
        vvod = self.pole_valyuty.get().strip()
        try:
            gruppa, kod = map(str.strip, vvod.split(','))
            kod = kod.upper()
            if gruppa in self.gruppy_valyut:
                if kod not in self.gruppy_valyut[gruppa]:
                    self.gruppy_valyut[gruppa].append(kod)
                    self.sohranit_gruppy_valyut()
                    self.vivod_valyut(f"Валюта {kod} добавлена в '{gruppa}'.")
                else:
                    self.vivod_valyut("Валюта уже есть в группе.")
            else:
                self.vivod_valyut("Такой группы не существует.")
        except ValueError:
            messagebox.showwarning("Внимание", "Используйте формат: Название,КОД (например МояГруппа,USD)")

    def udalit_iz_gruppy(self):
        vvod = self.pole_valyuty.get().strip()
        try:
            gruppa, kod = map(str.strip, vvod.split(','))
            kod = kod.upper()
            if gruppa in self.gruppy_valyut and kod in self.gruppy_valyut[gruppa]:
                self.gruppy_valyut[gruppa].remove(kod)
                self.sohranit_gruppy_valyut()
                self.vivod_valyut(f"Валюта {kod} удалена из '{gruppa}'.")
            else:
                self.vivod_valyut("Группа не найдена или в ней нет такой валюты.")
        except ValueError:
            messagebox.showwarning("Внимание", "Используйте формат: Название,КОД")

    def nastroit_vkladku_github(self):
        freym_github = tk.Frame(self.vkladka_github)
        freym_github.pack(pady=10)

        tk.Label(freym_github, text="Имя пользователя или запрос для поиска:").grid(row=0, column=0, columnspan=3,
                                                                                    pady=5)
        self.pole_github = tk.Entry(freym_github, width=40, font=("Arial", 12))
        self.pole_github.grid(row=1, column=0, columnspan=3, pady=5)

        tk.Button(freym_github, text="Профиль", command=self.github_profil, width=15).grid(row=2, column=0, padx=5,
                                                                                           pady=5)
        tk.Button(freym_github, text="Репозитории", command=self.github_repozitorii, width=15).grid(row=2, column=1,
                                                                                                    padx=5, pady=5)
        tk.Button(freym_github, text="Поиск", command=self.github_poisk, width=15).grid(row=2, column=2, padx=5, pady=5)

        self.tekst_github = scrolledtext.ScrolledText(self.vkladka_github, width=90, height=22, font=("Consolas", 10))
        self.tekst_github.pack(padx=10, pady=5)

    def vivod_github(self, tekst):
        self.tekst_github.delete(1.0, tk.END)
        self.tekst_github.insert(tk.END, tekst)

    def github_profil(self):
        imya = self.pole_github.get().strip()
        if not imya:
            return
        threading.Thread(target=self.potok_github_profil, args=(imya,), daemon=True).start()

    def potok_github_profil(self, imya):
        url = f"https://api.github.com/users/{imya}"
        zagolovki = {"Accept": "application/vnd.github+json"}
        try:
            otvet = requests.get(url, headers=zagolovki, timeout=5)
            if otvet.status_code == 200:
                dannie = otvet.json()
                rezultat = f"Профиль: {dannie.get('name', 'Не указано')}\n"
                rezultat += f"Ссылка: {dannie.get('html_url')}\n"
                rezultat += f"Репозитории: {dannie.get('public_repos')}\n"
                rezultat += f"Подписки: {dannie.get('following')} | Подписчики: {dannie.get('followers')}\n"
                self.koren.after(0, lambda: self.vivod_github(rezultat))
            else:
                self.koren.after(0, lambda: self.vivod_github("Пользователь не найден."))
        except Exception as e:
            self.koren.after(0, lambda: self.vivod_github(f"Ошибка сети: {e}"))

    def github_repozitorii(self):
        imya = self.pole_github.get().strip()
        if not imya:
            return
        threading.Thread(target=self.potok_github_repozitorii, args=(imya,), daemon=True).start()

    def potok_github_repozitorii(self, imya):
        url = f"https://api.github.com/users/{imya}/repos"
        try:
            otvet = requests.get(url, timeout=5)
            if otvet.status_code == 200:
                dannie = otvet.json()
                if not dannie:
                    self.koren.after(0, lambda: self.vivod_github("Нет публичных репозиториев."))
                    return
                rezultat = ""
                for repo in dannie:
                    rezultat += f"Название: {repo.get('name')}\n"
                    rezultat += f"Ссылка: {repo.get('html_url')}\n"
                    rezultat += f"Язык: {repo.get('language')} | Ветка: {repo.get('default_branch')}\n"
                    rezultat += "-" * 40 + "\n"
                self.koren.after(0, lambda: self.vivod_github(rezultat))
            else:
                self.koren.after(0, lambda: self.vivod_github("Ошибка доступа или пользователь не найден."))
        except Exception:
            self.koren.after(0, lambda: self.vivod_github("Ошибка сети."))

    def github_poisk(self):
        zapros = self.pole_github.get().strip()
        if not zapros:
            return
        threading.Thread(target=self.potok_github_poisk, args=(zapros,), daemon=True).start()

    def potok_github_poisk(self, zapros):
        url = f"https://api.github.com/search/repositories?q={zapros}"
        try:
            otvet = requests.get(url, timeout=5)
            if otvet.status_code == 200:
                dannie = otvet.json().get('items', [])
                if not dannie:
                    self.koren.after(0, lambda: self.vivod_github("Ничего не найдено."))
                    return
                rezultat = f"Топ результатов (макс 5):\n"
                for repo in dannie[:5]:
                    rezultat += f"Название: {repo.get('name')} (Автор: {repo.get('owner', {}).get('login')})\n"
                    rezultat += f"Ссылка: {repo.get('html_url')}\n"
                    rezultat += "-" * 40 + "\n"
                self.koren.after(0, lambda: self.vivod_github(rezultat))
            else:
                self.koren.after(0, lambda: self.vivod_github("Ошибка при поиске."))
        except Exception:
            self.koren.after(0, lambda: self.vivod_github("Ошибка сети."))

    def nastroit_vkladku_tcp(self):
        self.server_rabotaet = False
        self.server_soket = None
        self.klyuch_shifrovaniya = 42

        freym_tcp = tk.Frame(self.vkladka_tcp)
        freym_tcp.pack(pady=10)

        self.metka_status_servera = tk.Label(freym_tcp, text="Сервер выключен", fg="red", font=("Arial", 14))
        self.metka_status_servera.grid(row=0, column=0, columnspan=2, pady=10)

        tk.Button(freym_tcp, text="Запустить сервер", command=self.zapustit_server_tcp, width=20).grid(row=1, column=0,
                                                                                                       padx=5, pady=5)
        tk.Button(freym_tcp, text="Остановить сервер", command=self.ostanovit_server_klientom, width=20).grid(row=1,
                                                                                                              column=1,
                                                                                                              padx=5,
                                                                                                              pady=5)

        tk.Label(freym_tcp, text="Имя файла (.json / .xml / .bin):").grid(row=2, column=0, columnspan=2, pady=10)
        self.pole_fayla_tcp = tk.Entry(freym_tcp, width=40, font=("Arial", 12))
        self.pole_fayla_tcp.grid(row=3, column=0, columnspan=2, pady=5)
        self.pole_fayla_tcp.insert(0, "data.json")

        tk.Button(freym_tcp, text="Отправить файл (Клиент)", command=self.otpravit_fayl_klientom, width=20).grid(row=4,
                                                                                                                 column=0,
                                                                                                                 padx=5,
                                                                                                                 pady=5)
        tk.Button(freym_tcp, text="Скачать файл (Клиент)", command=self.skachat_fayl_klientom, width=20).grid(row=4,
                                                                                                              column=1,
                                                                                                              padx=5,
                                                                                                              pady=5)

        self.tekst_tcp = scrolledtext.ScrolledText(self.vkladka_tcp, width=90, height=15, font=("Consolas", 10))
        self.tekst_tcp.pack(padx=10, pady=5)

    def vivod_tcp(self, tekst):
        self.tekst_tcp.insert(tk.END, tekst + "\n")
        self.tekst_tcp.yview(tk.END)

    def algoritm_xor(self, dannie):
        rezultat = bytearray()
        for bayt in dannie:
            rezultat.append(bayt ^ self.klyuch_shifrovaniya)
        return bytes(rezultat)

    def zapustit_server_tcp(self):
        if self.server_rabotaet:
            return
        threading.Thread(target=self.potok_servera_tcp, daemon=True).start()

    def potok_servera_tcp(self):
        self.server_soket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server_soket.bind(('127.0.0.1', 5000))
            self.server_soket.listen(5)
            self.server_rabotaet = True

            self.koren.after(0, lambda: self.metka_status_servera.config(text="Сервер работает", fg="green"))
            self.koren.after(0, lambda: self.vivod_tcp("-> СЕРВЕР: Запущен на порту 5000."))

            while self.server_rabotaet:
                try:
                    klientskiy_soket, adres = self.server_soket.accept()
                    zapros = klientskiy_soket.recv(4096).decode('utf-8')
                    if not zapros:
                        klientskiy_soket.close()
                        continue

                    chasti = zapros.split('|')
                    komanda = chasti[0]

                    if komanda == 'OSTANOVIT':
                        klientskiy_soket.send("Uspeshno".encode('utf-8'))
                        self.server_rabotaet = False
                        self.koren.after(0, lambda: self.vivod_tcp("-> СЕРВЕР: Получена команда остановки."))
                        klientskiy_soket.close()
                        break

                    elif komanda == 'ZAGRUZIT':
                        imya = chasti[1]
                        razmer = int(chasti[2])
                        klientskiy_soket.send("GOTOV".encode('utf-8'))

                        polucheno = b""
                        while len(polucheno) < razmer:
                            chast = klientskiy_soket.recv(4096)
                            if not chast:
                                break
                            polucheno += chast

                        koren_imeni, rasshirenie = os.path.splitext(imya)
                        uspeshno = False
                        try:
                            tekst = polucheno.decode('utf-8')
                            if rasshirenie == '.json':
                                json.loads(tekst)
                                uspeshno = True
                            elif rasshirenie == '.xml':
                                ET.fromstring(tekst)
                                uspeshno = True
                        except Exception:
                            uspeshno = False

                        if uspeshno:
                            shifr = self.algoritm_xor(polucheno)
                            novoe_imya = f"{koren_imeni}.bin"
                            with open(novoe_imya, 'wb') as f:
                                f.write(shifr)
                            klientskiy_soket.send("Uspeshno".encode('utf-8'))
                            self.koren.after(0, lambda n=novoe_imya: self.vivod_tcp(
                                f"-> СЕРВЕР: Файл валидирован и зашифрован как {n}"))
                        else:
                            klientskiy_soket.send("Oshibka".encode('utf-8'))
                            self.koren.after(0, lambda: self.vivod_tcp("-> СЕРВЕР: Ошибка валидации файла."))

                    elif komanda == 'SKACHAT':
                        imya = chasti[1]
                        if os.path.exists(imya):
                            razmer = os.path.getsize(imya)
                            klientskiy_soket.send(f"GOTOV|{razmer}".encode('utf-8'))
                            otvet = klientskiy_soket.recv(4096).decode('utf-8')
                            if otvet == "NACHINAY":
                                with open(imya, 'rb') as f:
                                    klientskiy_soket.sendall(f.read())
                                self.koren.after(0, lambda i=imya: self.vivod_tcp(f"-> СЕРВЕР: Файл {i} отправлен."))
                        else:
                            klientskiy_soket.send("Oshibka".encode('utf-8'))
                            self.koren.after(0, lambda: self.vivod_tcp("-> СЕРВЕР: Файл не найден."))

                except Exception:
                    pass
                finally:
                    try:
                        klientskiy_soket.close()
                    except:
                        pass
        except Exception as oshibka:
            self.koren.after(0, lambda: self.vivod_tcp(f"-> СЕРВЕР ОШИБКА: {oshibka}"))
        finally:
            if self.server_soket:
                self.server_soket.close()
            self.server_rabotaet = False
            self.koren.after(0, lambda: self.metka_status_servera.config(text="Сервер выключен", fg="red"))
            self.koren.after(0, lambda: self.vivod_tcp("-> СЕРВЕР: Завершил работу."))

    def ostanovit_server_klientom(self):
        try:
            soket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            soket.connect(('127.0.0.1', 5000))
            soket.send("OSTANOVIT".encode('utf-8'))
            soket.close()
        except Exception:
            self.vivod_tcp("-> КЛИЕНТ: Сервер уже выключен или недоступен.")

    def otpravit_fayl_klientom(self):
        imya = self.pole_fayla_tcp.get().strip()
        if not os.path.exists(imya):
            messagebox.showwarning("Внимание", "Файл не найден в папке программы.")
            return

        try:
            soket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            soket.connect(('127.0.0.1', 5000))
            razmer = os.path.getsize(imya)
            soket.send(f"ZAGRUZIT|{imya}|{razmer}".encode('utf-8'))

            otvet = soket.recv(4096).decode('utf-8')
            if otvet == "GOTOV":
                with open(imya, 'rb') as f:
                    soket.sendall(f.read())
                rezultat = soket.recv(4096).decode('utf-8')
                if rezultat == "Uspeshno":
                    self.vivod_tcp("-> КЛИЕНТ: Файл успешно отправлен и принят сервером.")
                else:
                    self.vivod_tcp("-> КЛИЕНТ: Сервер отклонил файл (ошибка валидации).")
            soket.close()
        except Exception as e:
            self.vivod_tcp(f"-> КЛИЕНТ ОШИБКА: {e}")

    def skachat_fayl_klientom(self):
        imya = self.pole_fayla_tcp.get().strip()
        try:
            soket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            soket.connect(('127.0.0.1', 5000))
            soket.send(f"SKACHAT|{imya}".encode('utf-8'))

            otvet = soket.recv(4096).decode('utf-8')
            if otvet.startswith("GOTOV"):
                razmer = int(otvet.split('|')[1])
                soket.send("NACHINAY".encode('utf-8'))

                polucheno = b""
                while len(polucheno) < razmer:
                    chast = soket.recv(4096)
                    if not chast:
                        break
                    polucheno += chast

                novoe_imya = f"skachano_{imya}"
                with open(novoe_imya, 'wb') as f:
                    f.write(polucheno)
                self.vivod_tcp(f"-> КЛИЕНТ: Файл успешно скачан и сохранен как {novoe_imya}")
            else:
                self.vivod_tcp("-> КЛИЕНТ: Файл на сервере не найден.")
            soket.close()
        except Exception as e:
            self.vivod_tcp(f"-> КЛИЕНТ ОШИБКА: {e}")


if __name__ == "__main__":
    okno = tk.Tk()
    prilozhenie = PrilozheniePrakticheskoy(okno)
    okno.mainloop()