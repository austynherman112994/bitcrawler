import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bitcrawler", # Replace with your own username
    version="0.0.4",
    author="Austyn Herman",
    author_email="austynherman112994@gmail.com",
    description="Crawling the web made easy.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/austynherman112994/bitcrawler",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'requests',
        'reppy',
        'beautifulsoup4',
        'validators'
    ],
    python_requires='>=3.6',
)
