"""
MemTrace - A Statistical Testing Framework for Memory Systems in LLM Agents
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="memtrace",
    version="1.0.0",
    author="Mahendra Gurjar",
    author_email="madhugurjar1706@gmail.com",
    description="A statistical testing framework for memory systems in LLM agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Mahendra1706/MemTrace",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=22.0",
            "mypy>=0.950",
            "flake8>=4.0",
        ],
        "viz": [
            "matplotlib>=3.5",
            "seaborn>=0.11",
        ],
    },
    entry_points={
        "console_scripts": [
            "memtrace=run:main",
        ],
    },
    keywords="llm agents memory testing diagnosis event-sourcing",
    project_urls={
        "Bug Reports": "https://github.com/Mahendra1706/MemTrace/issues",
        "Source": "https://github.com/Mahendra1706/MemTrace",
        "Documentation": "https://github.com/Mahendra1706/MemTrace#readme",
    },
)
