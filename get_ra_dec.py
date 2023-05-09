from bs4 import BeautifulSoup
from selenium import webdriver
import time

def get_ra_dec(driver, query):
    url = f'http://ned.ipac.caltech.edu/byname?objname={query}&hconst=67.8&omegam=0.308&omegav=0.692&wmap=4&corr_z=1'
    driver.get(url)
    time.sleep(10)
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
