from setuptools import setup

setup(
    name="announcer",
    version="0.1.0",
    packages=["announcer"],
    entry_points={
        "console_scripts": [
            "announcer=announcer.main:main",
        ],
    },
    install_requires=[
        "PyQT5",
        "requests",
        "audioplayer",
    ],
    package_data={
        "announcer": ["sounds/**"],
    }
)
