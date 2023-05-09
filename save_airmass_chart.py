from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By 
import time


def save_airmass_chart(target_list, date, screenshot_file="airmass_chart.png"):
    driver = webdriver.Chrome()

    driver.get("http://catserver.ing.iac.es/staralt/index.php")

    year, month, day = date.strftime("%Y-%B-%d").split("-")
    Select(driver.find_element(By.NAME, "form[day]")).select_by_visible_text(day)
    Select(driver.find_element(By.NAME, "form[month]")).select_by_visible_text(month)
    Select(driver.find_element(By.NAME, "form[year]")).select_by_visible_text(year)

    Select(driver.find_element(By.NAME, "form[obs_name]")).select_by_value("Mauna Kea Observatory (Hawaii, USA)")

    coord_string = "\n".join([
        f"{name.replace(' ', '')} {ra.replace('h', ' ').replace('m', ' ').replace('s', ' ')} {dec.replace('d', ' ').replace('m', ' ').replace('s', ' ')}"
        for name, (ra, dec) in target_list
    ])
    driver.find_element(By.NAME, "form[coordlist]").send_keys(coord_string)

    driver.find_element(By.NAME, "submit").click()

    time.sleep(3)
    driver.switch_to.window(driver.window_handles[-1])

    driver.save_screenshot(screenshot_file)

    driver.quit()
