from setuptools import setup

# This is the setup script for the cloud client application.
setup(
    name="cloud",
    version="0.1",
    py_modules=["main", "auth", "files", "admin", "utils"],
    install_requires=[
        "typer",
        "requests",
        "rich"
    ],
    entry_points={
        "console_scripts": [
            "cloud = main:main",
        ],
    },
)
