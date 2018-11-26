from setuptools import setup, find_packages
from os import path

setup(
    name='autoasd', 
    version='0.0.1',
    description='Control ASD spectroscopy software remotely.',
    url='https://github.com/kathleenhoza/autoasd',  # Optional

    author='Kathleen Hoza', 
    author_email='hozak@wwu.edu',  # Optional

    classifiers=[  
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Spectroscopists',
        'Programming Language :: Python :: 3',
    ],

    keywords='ASD ViewSpecPro RS3 spectroscopy automation',  # Optional

    packages=['autoasd'],  # Required

    install_requires=['time','os','imp','sys','datetime','shutil','pywinauto','datetime','pyautogui'],

)