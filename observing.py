import argparse
import time
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from astropy.coordinates import SkyCoord
from astropy.time import Time
from astropy import units as u
import ephem
from astroplan import Observer, FixedTarget

def get_ra_dec(driver, query):
    url = f'http://ned.ipac.caltech.edu/byname?objname={query}&hconst=67.8&omegam=0.308&omegav=0.692&wmap=4&corr_z=1'
    driver.get(url)
    time.sleep(10)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    row = soup.find('tr', {'class': 'ov_insiderow ov_inside_coord_row'})

    if row:
        ra_span = row.find('span', {'id': 'allbyname_7'})
        dec_span = row.find('span', {'id': 'allbyname_8'})
        if ra_span:
            ra = ra_span.text.strip()
        if dec_span:
            dec = dec_span.text.strip()
        return ra, dec
    else:
        return None, None

def main(targets):
    observing_location = Observer(longitude=-155.0903 * u.deg,
                                  latitude=19.7026 * u.deg,
                                  elevation=4205 * u.m,
                                  name="Mauna Kea")

    # Initialize the Selenium driver
    driver = webdriver.Chrome(ChromeDriverManager().install())

    ra_dec_list = [get_ra_dec(driver, target) for target in targets]

    # Quit the Selenium driver
    driver.quit()

    fixed_targets = [FixedTarget(coord=SkyCoord(ra=ra, dec=dec), name=name) for name, (ra, dec) in zip(targets, ra_dec_list)]

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

    print("RA and Dec values of targets:")
    for target, (ra, dec) in zip(targets, ra_dec_list):
        print(f"{target}: RA = {ra}, Dec = {dec}")

    print(f"\nThe best night for observing these targets, avoiding full moon, is: {best_day.to_datetime().strftime('%Y-%m-%d')}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find RA, Dec and the best night for observing targets.")
    parser.add_argument("targets", nargs="+", help="Space-separated list of target names")
    args = parser.parse_args()
    main(args.targets)
