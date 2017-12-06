
from setuptools import setup

setup(
    name='reminders',
    packages=['reminders'],
    include_package_data=True,
    install_requires=[
        'flask',
        'twilio',
    ],
)
