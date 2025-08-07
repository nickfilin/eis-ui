from modules import navigations
import requests
# Autohotkey module
from ahk import AHK
ahk = AHK()
# Selenuim modules
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os
# Получаем директорию, где находится скрипт
script_dir = os.path.dirname(os.path.abspath(__file__))
# Формируем путь к папке profile в той же директории
profile_dir = os.path.join(script_dir, "profile")
# Настройка опций Chrome
options = Options()
options.add_argument(f"--allow-profiles-outside-user-dir")
options.add_argument(f"--user-data-dir={profile_dir}")
options.add_argument(f"--start-maximized")
options.add_experimental_option("excludeSwitches", ['enable-automation'])
options.add_experimental_option("detach", True)
options.add_argument(f"--remote-debugging-port=9222")
options.add_argument(f"--no-default-browser-check")
options.page_load_strategy = 'none'
options.add_experimental_option("excludeSwitches", ["enable-logging"]) # помогло подавить логи
# Запуск драйвера
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
driver.get('https://demo.msk.muzkult.ru/cpa')
#driver.get('https://muz.helpdeskeddy.com/')
# Захват активной страницы
def get_activepage():
    request = requests.get("http://127.0.0.1:9222/json")
    j = request.json()
    found_tab = False    
    for el in j:
        if el["type"] == "page":  
            found_tab = el           
            break  
    handle = found_tab["id"]
    if driver.current_window_handle != handle:
       driver.switch_to.window(handle)
#==========================================================
def test1():
    pass
#==========================================================
ahk.add_hotkey('f6', callback=test1)
ahk.add_hotkey('F1', callback=lambda: print(navigations.process_url("https://rew.muzkult.ru")))
#==========================================================
ahk.start_hotkeys()  
ahk.block_forever()