import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="steam-reporter",
    version="1.0.0",
    author="Bryan Weissinger",
    description="Create database of steam market transactions from parsed from email confirmations.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bweissinger/steam-reporter",
    packages=setuptools.find_packages(),
    entry_points={
          'console_scripts': [
              'steam_reporter = steam_reporter.__main__:main'
          ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6'
)
