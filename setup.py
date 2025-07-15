"""
CoinCompass 설치 스크립트
"""

from setuptools import setup, find_packages
import os

# README 파일 읽기
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# requirements.txt 읽기
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="coincompass",
    version="1.0.0",
    author="gum798",
    author_email="gum798@users.noreply.github.com",
    description="🧭 스마트 암호화폐 투자 나침반 - AI 기반 시장 분석 플랫폼",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gum798/CoinCompass",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "black",
            "flake8",
            "mypy"
        ]
    },
    entry_points={
        "console_scripts": [
            "coincompass=coincompass.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "coincompass": [
            "config/*.json",
            "data/charts/.gitkeep",
            "data/reports/.gitkeep",
            "data/logs/.gitkeep",
            "data/cache/.gitkeep"
        ]
    },
    project_urls={
        "Bug Reports": "https://github.com/gum798/CoinCompass/issues",
        "Source": "https://github.com/gum798/CoinCompass",
        "Documentation": "https://github.com/gum798/CoinCompass/wiki",
    },
)