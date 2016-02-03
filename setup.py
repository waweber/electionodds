from setuptools import setup

setup(
    name="electionodds",
    version="1.0.0",
    py_modules=["electionodds"],

    install_requires=[
        "lxml",
        "cssselect",
        "requests",
    ],

)
