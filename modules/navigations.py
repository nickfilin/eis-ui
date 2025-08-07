import re
def printTest(message):
    print(message)
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
