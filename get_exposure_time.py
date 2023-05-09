from selenium.webdriver.common.by import By
import time 

def get_exposure_time(driver, magnitude, target_sn=50, wavelength=6000, max_iterations=10, tolerance=0.5):
    url = "http://etc.ucolick.org/web_s2n/lris"
    driver.get(url)

    # Fill in the object's magnitude
    magnitude_input = driver.find_element(By.NAME, "mag")
    magnitude_input.clear()
    magnitude_input.send_keys(str(magnitude))


    driver.find_element(By.NAME, "seeing").send_keys("0.7")
    driver.find_element(By.NAME, "slitwidth").send_keys("1.0")
    driver.find_element(By.NAME, "airmass").send_keys("1.8")

    sn = 0
    exposure_time = 100  # Initialize
    for _ in range(max_iterations):


        exposure_time_input = driver.find_element(By.NAME, "exptime")
        exposure_time_input.clear()
        exposure_time_input.send_keys(str(exposure_time))


        driver.find_element(by=By.CSS_SELECTOR, value="input[type='submit'][value='Compute exposure']").click()

        time.sleep(3)

        driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Show table of counts']").click()

        time.sleep(2)

        table_rows = driver.find_elements(By.XPATH, "//table[@id='ctstab']//tbody/tr")
        sn = None
        for row in table_rows:
            columns = row.find_elements(By.TAG_NAME, "td")
            if columns and float(columns[0].text) == wavelength:
                sn = float(columns[-1].text)
                break

        if sn is None:
            raise ValueError(f"Unable to find S/N at {wavelength} Å")


        if abs(sn - target_sn) <= tolerance:
            break

        exposure_time *= (target_sn / sn) ** 2


    return exposure_time, sn
