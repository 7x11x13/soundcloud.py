#!/usr/bin/env python

from distutils.core import setup


def readme():
    with open('README.md', encoding="UTF-8") as f:
        return f.read()

setup(
    name="soundcloud-v2",
    version="1.3.7",
    description="Python wrapper for the v2 SoundCloud API",
    long_description=readme(),
    long_description_content_type='text/markdown',
    author="7x11x13",
    author_email="x7x11x13@gmail.com",
    url="https://github.com/7x11x13/soundcloud.py",
    packages=["soundcloud", "soundcloud.resource"],
    install_requires=[
        "dacite",
        "python-dateutil>=2.8.2",
        "requests"
    ],
    extras_require={
        "test": ["coveralls", "pytest", "pytest-dotenv"]
    },
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires = ">=3.7",
    project_urls={
        "Bug Tracker": "https://github.com/7x11x13/soundcloud.py/issues"
    }
)
