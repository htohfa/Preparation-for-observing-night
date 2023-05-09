from .main import main
from .get_ra_dec import get_ra_dec
from .get_exposure_time import get_exposure_time

from selenium import webdriver

def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    return driver
