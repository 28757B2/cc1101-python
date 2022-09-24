import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cc1101-python",
    version="1.3.1",
    author="28757B2",
    description="Python interface to the CC1101 Linux device driver",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/28757B2/cc1101-python",
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "Topic :: Home Automation",
        "Operating System :: POSIX :: Linux",
        "Topic :: System :: Hardware :: Hardware Drivers",
        "License :: OSI Approved :: MIT License"
    ],
    entry_points={
        "console_scripts": {
            "cc1101 = cc1101.__main__:main"
        }
    }
)
