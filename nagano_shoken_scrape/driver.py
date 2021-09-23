from selenium import webdriver


def prepare_driver(headless=True) -> webdriver.Chrome:
    opt = webdriver.ChromeOptions()
    if headless:
        opt.add_argument("--headless")
    opt.add_argument("--no-sandbox")
    opt.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=opt)
    driver.set_window_size(1600, 900)
    return driver
