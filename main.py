import argparse
import numpy as np 
from astropy.coordinates import Angle
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from astropy.coordinates import SkyCoord
from astropy.time import Time
from astropy import units as u
import ephem
from astroplan import Observer, FixedTarget
from .get_ra_dec import get_ra_dec
from .get_exposure_time import get_exposure_time
from .save_airmass_chart import save_airmass_chart

def main(targets):
    observing_location = Observer(longitude=-155.0903 * u.deg,
                                  latitude=19.7026 * u.deg,
                                  elevation=4205 * u.m,
                                  name="Mauna Kea")

    # Initialize
    driver = webdriver.Chrome(ChromeDriverManager().install())

    #ra_dec_list = [get_ra_dec(driver, target) for target in targets]
    ra_dec_mag_list = [get_ra_dec(driver, target) for target in targets]


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

    # moon_phases
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


def run():
    parser = argparse.ArgumentParser(description="Find RA, Dec and the best night for observing targets.")
    parser.add_argument("targets", nargs="+", help="Space-separated list of target names")
    args = parser.parse_args()
    main(args.targets)
