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

git clone https://github.com/htohfa/observing-night.git


pip install automate_observing


## How to use

After installing the automate_observing package, navigate to the directory where automate_observing is installed in the command prompt and execute 
<span style="color:green">automate_observing 'RBS 1303' '3C 319'</span>


For using other functions such as exposure_time and get_ra_dec:


<span style="color:blue">
  
  
> import automate_observing as ao
  
  
> driver = ao.create_driver()
  
  
> ra_dec_mag = ao.get_ra_dec(driver, "RBS 1303") => Positional arguments: Driver, targets
  
  
> print(ra_dec_mag) => ('13h41m12.904s', '-14d38m40.58s', '13.4')
  
  
> exposure_time,sn = ao.get_exposure_time(driver,15, target_sn=60)     => Positional arguments: Driver, Magnitude; Keyword arguemts: target_sn=50, wavelength=6000, max_iterations=10, tolerance=0.5
  
  
</span>



