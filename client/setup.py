from setuptools import setup

setup(
    name="cloudcli",
    version="0.1",
    py_modules=["main", "auth", "file", "utils"],
    install_requires=[
        "typer",
        "requests",
        "rich"
    ],
    entry_points={
        "console_scripts": [
            "cloudcli = main:main",
        ],
    },
)
