#!/usr/bin/env python

from distutils.core import setup


def readme():
    with open("README.md", encoding="UTF-8") as f:
        return f.read()


setup(
    name="soundcloud-v2",
    version="1.6.0",
    description=(
        "Python wrapper for the internal v2 SoundCloud API."
        "Does not require an API key."
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
        "requests",
        "typing_extensions; python_version<'3.8'",
    ],
    extras_require={
        "dev": [
            "coveralls",
            "pytest",
            "pytest-dotenv",
            "types-python-dateutil",
            "types-requests",
            "mypy",
            "ruff",
        ],
        "docs": ["pdoc"],
    },
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    project_urls={"Bug Tracker": "https://github.com/7x11x13/soundcloud.py/issues"},
)
