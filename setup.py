from pathlib import Path

import setuptools

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    name="streamlit_p5",
    version="0.0.4",
    author="Neal Riley",
    author_email="neal.riley@gmail.com",
    description="Bring the power of ProcessingJS (aka P5) to Streamlit. This module allows you to create Processing sketches, interact with those sketches using the mouse and keyboard, and share data between your Processing Sketch and Stremalit.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://streamlit-p5-examples.fly.dev/",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.7",
    install_requires=[
        "streamlit >= 0.63",
    ],
    extras_require={
        "devel": [
            "wheel",
            "pytest==7.4.0",
            "playwright==1.39.0",
            "requests==2.31.0",
            "pytest-playwright-snapshot==1.0",
            "pytest-rerunfailures==12.0",
        ]
    }
)
