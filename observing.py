import argparse
import time
import numpy as np
from bs4 import BeautifulSoup
from astropy.coordinates import Angle
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from astropy.coordinates import SkyCoord
from astropy.time import Time
from astropy import units as u
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import ephem
from astroplan import Observer, FixedTarget

def get_ra_dec(driver, query):
    url = f'http://ned.ipac.caltech.edu/byname?objname={query}&hconst=67.8&omegam=0.308&omegav=0.692&wmap=4&corr_z=1'
    driver.get(url)
    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    ra = dec = mag = None

    coord_row = soup.find('tr', {'class': 'ov_insiderow ov_inside_coord_row'})
    if coord_row:
        ra_span = coord_row.find('span', {'id': 'allbyname_7'})
        dec_span = coord_row.find('span', {'id': 'allbyname_8'})
        if ra_span:
            ra = ra_span.text.strip()
        if dec_span:
            dec = dec_span.text.strip()

    mag_row = soup.find('tr', {'class': 'ov_insiderow ov_inside_photom_row_3'})
    if mag_row:
        mag_span = mag_row.find('span', {'id': 'allbyname_53'})

        if mag_span:
            mag = mag_span.text.strip().split()[0]

    return ra, dec, mag



def get_exposure_time(driver, magnitude, target_sn=50, wavelength=6000, max_iterations=10, tolerance=0.5):
    url = "http://etc.ucolick.org/web_s2n/lris"
    driver.get(url)

    # Fill in the object's magnitude
    magnitude_input = driver.find_element(By.NAME, "mag")
    magnitude_input.clear()
    magnitude_input.send_keys(str(magnitude))

    # Set other parameters
    # You may need to adjust these to match your requirements
    driver.find_element(By.NAME, "seeing").send_keys("0.7")
    driver.find_element(By.NAME, "slitwidth").send_keys("1.0")

    sn = 0
    exposure_time = 100  # Initial guess for exposure time in seconds
    for _ in range(max_iterations):
        # Update the exposure time
        exposure_time_input = driver.find_element(By.NAME, "exptime")
        exposure_time_input.clear()
        exposure_time_input.send_keys(str(exposure_time))

        # Click the Compute button
        #driver.find_element_by_css_selector("input[type='submit'][value='Compute exposure']").click()
        driver.find_element(by=By.CSS_SELECTOR, value="input[type='submit'][value='Compute exposure']").click()

        # Get the S/N at the desired wavelength
        time.sleep(3)  # Give the plot some time to update



        driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Show table of counts']").click()

        # Get the S/N at the desired wavelength
        time.sleep(2)  # Give the table some time to load

        table_rows = driver.find_elements(By.XPATH, "//table[@id='ctstab']//tbody/tr")
        sn = None
        for row in table_rows:
            columns = row.find_elements(By.TAG_NAME, "td")
            if columns and float(columns[0].text) == wavelength:
                sn = float(columns[-1].text)
                break

        if sn is None:
            raise ValueError(f"Unable to find S/N at {wavelength} Å")

        # Check if the S/N is close enough to the target S/N
        if abs(sn - target_sn) <= tolerance:
            break

        # Update the exposure time based on the current S/N
        exposure_time *= (target_sn / sn) ** 2


    return exposure_time, sn







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





def main(targets):
    observing_location = Observer(longitude=-155.0903 * u.deg,
                                  latitude=19.7026 * u.deg,
                                  elevation=4205 * u.m,
                                  name="Mauna Kea")

    # Initialize the Selenium driver
    driver = webdriver.Chrome(ChromeDriverManager().install())

    #ra_dec_list = [get_ra_dec(driver, target) for target in targets]
    ra_dec_mag_list = [get_ra_dec(driver, target) for target in targets]


    # Quit the Selenium driver
    driver.quit()


    #fixed_targets = [FixedTarget(coord=SkyCoord(ra=ra, dec=dec), name=name) for name, (ra, dec) in zip(targets, ra_dec_list)]
    fixed_targets = [FixedTarget(coord=SkyCoord(ra=ra, dec=dec), name=name) for name, (ra, dec, _) in zip(targets, ra_dec_mag_list)]


    start_time = Time("2023-04-01 00:00:00")
    end_time = Time("2023-06-14 00:00:00")
    n_days = int((end_time - start_time).value)

    daily_airmass = np.full((len(fixed_targets), n_days), np.inf)
    time_intervals_per_day = 24
    for i, target in enumerate(fixed_targets):
        for j in range(n_days):
            for k in range(time_intervals_per_day):
                observing_time = start_time + j * u.day + k * u.hour
                observing_local_time = observing_location.astropy_time_to_datetime(observing_time)
                if 17 <= observing_local_time.hour < 5 or observing_location.is_night(observing_time):
                    airmass = observing_location.altaz(observing_time, target).secz
                    daily_airmass[i, j] = min(airmass, daily_airmass[i, j])

    # Add moon phase checking and avoiding full moon nights
    moon = ephem.Moon()
    moon_phases = np.zeros(n_days)

    for j in range(n_days):
        observing_time = start_time + j * u.day
        observing_time_datetime = observing_time.to_datetime()
        moon.compute(observing_time_datetime)
        moon_phases[j] = moon.moon_phase

    full_moon_mask = (moon_phases > 0.95)
    avg_airmass = np.mean(daily_airmass, axis=0)
    avg_airmass[full_moon_mask] = np.inf
    best_day_idx = np.argmin(avg_airmass)
    best_day = start_time + best_day_idx * u.day

    driver = webdriver.Chrome(ChromeDriverManager().install())
    print("RA, Dec, Magnitude, Exposure Time, and S/N values of targets:")
    print("Name         RA (hh mm ss)    Dec (±dd mm ss)    Magnitude    Exposure Time    S/N")
    for target, (ra, dec, mag) in zip(targets, ra_dec_mag_list):
        ra_coord = Angle(ra, unit=u.hour).to_string(unit=u.hour, sep=' ', precision=1)
        dec_coord = Angle(dec, unit=u.deg).to_string(unit=u.deg, sep=' ', precision=1, alwayssign=True)

        # Calculate the exposure time and S/N
        exposure_time, sn = get_exposure_time(driver, mag)

        print(f"{target: <12} {ra_coord: <15} {dec_coord: <15}     {mag: <10}   {exposure_time: <14.2f}   {sn:.2f}")

    driver.quit()

    print(f"\nThe best night for observing these targets, avoiding full moon, is: {best_day.to_datetime().strftime('%Y-%m-%d')}")

    print("Saving airmass chart for all targets...")
    save_airmass_chart(list(zip(targets, [(ra, dec) for ra, dec, mag in ra_dec_mag_list])), best_day.to_datetime(), screenshot_file="airmass_chart.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find RA, Dec and the best night for observing targets.")
    parser.add_argument("targets", nargs="+", help="Space-separated list of target names")
    args = parser.parse_args()
    main(args.targets)
