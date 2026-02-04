"""Setup configuration for ENS160 library."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="ens160",
    version="0.1.0",
    author="Haneef Rahman",
    description="Python library to interface with ScioSense ENS160 Digital Metal-Oxide Multi-Gas Sensor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Haneef-Rahman/ENS160",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: System :: Hardware :: Hardware Drivers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "smbus2>=0.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=3.0",
        ],
    },
    keywords="ens160 sensor i2c air-quality tvoc eco2 aqi gas-sensor",
    project_urls={
        "Bug Reports": "https://github.com/Haneef-Rahman/ENS160/issues",
        "Source": "https://github.com/Haneef-Rahman/ENS160",
    },
)
