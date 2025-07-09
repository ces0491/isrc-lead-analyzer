# setup.py
"""
Setup configuration for Precise Digital Lead Generation Tool
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="precise-digital-leads",
    version="1.0.0",
    author="Precise Digital",
    author_email="contact@precise.digital",
    description="Lead generation tool for independent music artists",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/precise-digital/lead-generation-tool",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Other Audience",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Flask>=2.3.0",
        "Flask-CORS>=4.0.0",
        "python-dotenv>=1.0.0",
        "SQLAlchemy>=2.0.0",
        "requests>=2.31.0",
        "aiohttp>=3.8.0",
        "redis>=5.0.0",
        "pandas>=2.1.0",
        "python-dateutil>=2.8.0",
        "asyncio-throttle>=1.0.0",
        "spotipy>=2.23.0",
        "beautifulsoup4>=4.12.0",
        "Werkzeug>=2.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.7.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "precise-digital-leads=run:main",
        ],
    },
)
