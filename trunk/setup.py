# Numbler setup script

from setuptools import setup, find_packages

setup(
    name = "Numbler",
    version = "0.1",
    url = 'http://numbler.com',
    author_email = 'carl@numbler.com',
    # use MANIFEST.in
    include_package_data = True,
    packages = find_packages(),
    zip_safe=False
    )
