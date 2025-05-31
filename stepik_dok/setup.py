from setuptools import setup, find_packages

setup(
    name="html_processor",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "reportlab>=4.0.4",
        "beautifulsoup4>=4.12.2",
        "matplotlib>=3.7.1",
        "lxml>=4.9.3"
    ],
    python_requires='>=3.7'
)