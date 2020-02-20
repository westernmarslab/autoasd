from setuptools import setup, find_packages
from os import path

with open("README.txt", "r") as fh:
    long_description = fh.read()

setup(
    name='AutoAsd', 
    version='0.2.7',
    description='Automation script for ASD spectroscopy software.',
    #long_description=long_description,
    url='https://github.com/kathleenhoza/autoasd',  # Optional

    author='Kathleen Hoza', 
    author_email='hozak@wwu.edu',  # Optional

    classifiers=[  
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
    ],

    keywords='ASD ViewSpecPro RS3 spectroscopy automation',  # Optional

    packages=['autoasd'],  # Required

    package_data={
        'autoasd': ['img/*','img2/*','spectralon_data/*']
    },

    install_requires=['pywinauto','pyautogui'],
    python_requires='>=3'

)