from setuptools import setup, find_packages

setup(
    name="red-whisperer",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "pytest>=7.4.0",
        "pytest-cov>=4.1.0",
        "black>=23.7.0",
        "flake8>=6.1.0",
        "mypy>=1.5.0",
        "types-requests>=2.31.0.1"
    ],
    python_requires=">=3.8",
    author="Zeevik98",
    author_email="your.email@example.com",
    description="AI-Powered Security Testing Framework",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Zeevik98/RW4WEB",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
) 