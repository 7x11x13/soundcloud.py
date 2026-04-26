#!/usr/bin/env python

from setuptools import setup  # type: ignore[import-untyped]


def readme():
    with open("README.md", encoding="UTF-8") as f:
        return f.read()


setup(
    name="soundcloud-v2",
    version="1.7.0",
    description=(
        "Python wrapper for the internal v2 SoundCloud API.Does not require an API key."
    ),
    long_description=readme(),
    long_description_content_type="text/markdown",
    author="7x11x13",
    author_email="x7x11x13@gmail.com",
    url="https://github.com/7x11x13/soundcloud.py",
    packages=["soundcloud", "soundcloud.resource"],
    package_data={"soundcloud": ["py.typed"]},
    install_requires=[
        "dacite>=1.8.1",
        "python-dateutil>=2.8.2",
        "curl_cffi>=0.10,<0.16",
    ],
    extras_require={
        "dev": [
            "coveralls",
            "pytest",
            "pytest-dotenv",
            "types-python-dateutil",
            "mypy",
            "ruff",
        ],
        "docs": ["pdoc"],
    },
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    project_urls={"Bug Tracker": "https://github.com/7x11x13/soundcloud.py/issues"},
)
