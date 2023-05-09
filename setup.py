from setuptools import setup, find_packages

setup(
    name="automate_observing",
    version="0.1",
    description="Astronomical tools for RA, Dec, airmass chart, and exposure time.",
    author="Hurum Maksora Tohfa",
    author_email="your.email@example.com",
    url="http://github.com/yourusername/astro_tools",
    packages=find_packages(),
    install_requires=[
        "argparse",
        "numpy",
        "beautifulsoup4",
        "astropy",
        "selenium",
        "webdriver_manager",
        "ephem",
        "astroplan",
    ],
    entry_points={
        'console_scripts': [
            'automate_observing=automate_observing.main:run',
        ],
    },
)
