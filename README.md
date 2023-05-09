# Observing night with Python
The automate-observing package is a Python package that provides functionality for observers to automate their telescope observations. It can generate a list of Right Ascension (RA), Declination (Dec), and visible magnitude of targets and also calculate the best night for observing and calculates exposure time for achieving a Signal-to-Noise ratio (S/N) of 50 and save an airmass chart.

The package also allows users to extract RA, Dec, and magnitude information for specific targets, without calculating exposure times. The exposure time function is fully optimazable to users needs i.e. users can adjust the S/N ratio, wavelength, maximum iteration, and tolerance while calculating the exposure time. This makes the package a powerful tool for observers who want to optimize their observations and reduce manual effort.

## Required packages
- NumPy
- Astropy
- Astroplan
- Selenium
- Webdriver_manager

## Installation

pip install automate_observing



