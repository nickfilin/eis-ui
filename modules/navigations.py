#pip install selenium pyperclip
import re
import time
import pyperclip
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

#Проверяет, содержит ли строка валидный URL 
def is_valid_url(url):   
    # проверка, является ли строкой 
    if not url or not isinstance(url, str):
        return False
    #удаление пробелов в конце и начале слова
    url = url.strip()    
    # Проверяем начало URL на наличие протокола
    if not url.startswith(('http://', 'https://')):
        return False
    # Проверяем запрещенные пути
    forbidden_paths = ['/vk.com/', '/ok.ru/', 'youtube', 'https://t.me/']
    if any(forbidden.lower() in url.lower() for forbidden in forbidden_paths):
        return False
    
    # Проверяем доменную зону (с учетом возможных путей после домена)
    domain_pattern = re.compile(
        r'^(https?:\/\/)'  # протокол (обязательный)
        r'([\da-zа-яё-]+\.)+'  # поддомены
        r'([\da-zа-яё-]+)'  # домен
        r'(\.(ru|рф|рус))'  # доменная зона
        r'(\/[\w\/-]*)?$',  # необязательный путь
        re.IGNORECASE
    )
    
    return bool(domain_pattern.match(url))

def extract_base_url(url):
    """Очищает URL от лишних частей и возвращает базовый домен"""
    if not url:
        return None
    
    url = url.strip()
    
    # Удаляем параметры запроса и якоря
    url = url.split('?')[0].split('#')[0]
    
    # Удаляем завершающие слэши и конкретные пути
    url = re.sub(r'(\/+\s*|\/about|\/cpa|\/[\w-]+\/?)$', '', url)
    
    return url

def get_url_from_iframe(driver):
    """Получает URL из iframe или ожидает ввода пользователя"""
    try:
        # Ждем загрузки iframe и переключаемся на него
        iframe = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".iframe-dialog__iframe iframe"))
        )
        driver.switch_to.frame(iframe)

        # Ищем все элементы с текстом заметок - более надежный поиск
        note_elements = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".note table .note-text"))
        )

        found_urls = []
        for element in note_elements:
            text = element.text.strip()
            print(f"Найден текст в элементе: {text}")  # Отладочный вывод
            
            if is_valid_url(text):
                print(f"Найден валидный URL: {text}")  # Отладочный вывод
                found_urls.append(text)

        # Возвращаемся к основному контенту
        driver.switch_to.default_content()

        if len(found_urls) == 1:
            return extract_base_url(found_urls[0])
        
        print(f"Найдено URL: {len(found_urls)} - {found_urls}")  # Отладочный вывод
        return None

    except Exception as e:
        print(f"Ошибка при поиске URL в iframe: {str(e)}")
        driver.switch_to.default_content()
        return None

def wait_for_url_in_clipboard(timeout=60):
    """Ожидает, пока пользователь скопирует валидный URL в буфер обмена"""
    print("Ожидаю URL в буфере обмена...")
    start_time = time.time()
    last_value = pyperclip.paste()
    
    while time.time() - start_time < timeout:
        try:
            current_value = pyperclip.paste().strip()
            if current_value != last_value:
                print(f"Обнаружено изменение буфера: {current_value}")
                if is_valid_url(current_value):
                    print(f"Валидный URL найден в буфере: {current_value}")
                    return extract_base_url(current_value)
                last_value = current_value
        except Exception as e:
            print(f"Ошибка при проверке буфера обмена: {e}")
        
        time.sleep(0.5)
    
    raise TimeoutError("Пользователь не скопировал URL в течение заданного времени")

def open_task(driver):    
    """Основная функция обработки задачи"""
    try:
        # Получаем email и номер задачи
        email = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.ticket-user__field-value-text'))
        )[1].text
        number_task = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.ticket-detail__unique-id strong'))
        ).text
        print(f"Email: {email}, Номер задачи: {number_task}")
        
        # Клик по кнопке для открытия iframe
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "hde-info-btn"))
        ).click()
        
        # Получаем URL из iframe
        tmp_url = get_url_from_iframe(driver)
        
        # Если URL не найден, ждем ввода пользователя
        if not tmp_url:
            print("Подходящий URL не найден автоматически. Ожидаю ввод пользователя...")
            try:
                tmp_url = wait_for_url_in_clipboard()
                print(f"Получен URL из буфера обмена: {tmp_url}")
            except TimeoutError as e:
                print(e)
                return
        
        # Формируем итоговый URL
        final_url = tmp_url.rstrip('/') + "/cpa"
        print(f"Открываю URL: {final_url}")
        
        
       ###### Открываем URL в новой вкладке ########
        driver.execute_script(f"window.open('{final_url}', '_blank');")
       
        # Переключаемся на новую вкладку
        driver.switch_to.window(driver.window_handles[-1])
        
        try:
            email = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.btn-block'))
            )
            email.click()
            print("Кнопка найдена и нажата.")
        except TimeoutException:
            print("Кнопка с классом .btn-block не найдена за отведённое время.")

        driver.find_element(By.CSS_SELECTOR, ".btn-block").click()
        time.sleep(2)
        current_url = driver.current_url
        print(f"Текущий URL: {current_url}")
    except Exception as e:
        print(f"Ошибка в функции open_task: {str(e)}")
        raise

#################### Открытие страниц ####################################### 
def open_page(driver, url, url_end=""):
    url = url + url_end
    driver.switch_to.new_window('tab')
    driver.get(url)
def process_url(url):
    urls_dictated_pages = ""  # по умолчанию пустая строка
    if re.search(r"muzkult\.ru", url):
        urls_dictated_pages = [
            "9096144", "9096140", "9096160", "9096152", "9096148", "9096154",
            "9096150", "9096156", "9096146", "9096138", "9096158", "9096142",
            "48421415", "48421393", "83452567", "112404983"
        ]
    elif re.search(r"eduru\.ru", url):
        urls_dictated_pages = [
            "7547824", "7547814", "7547822", "7547808", "7547818", "7547812",
            "7547804", "7547826", "7547806", "7547820", "7547810", "7547816",
            "48423812", "48423779", "83460010", "112332060", "112332099"
        ]
    elif re.search(r"prosadiki\.ru", url):
        urls_dictated_pages = [
            "8318369", "8318363", "8318365", "8318361", "8318377", "8318359",
            "8318379", "8318375", "8318357", "8318371", "8318367", "8318373",
            "48423729", "48423752", "83460937", "112305154"
        ]
    else: urls_dictated_pages = None
    return urls_dictated_pages
