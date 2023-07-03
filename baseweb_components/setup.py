import setuptools

setuptools.setup(
    name="streamlit_baseweb",
    version="0.0.1",
    author="Thomas Bouamoud",
    author_email="thomas.bouamoud@gmail.com",
    description="A Streamlit implementation of the Base Web library.",
    long_description="https://baseweb.design/",
    long_description_content_type="text/plain",
    url="https://github.com/thomasbs17/streamlit-contributions/baseweb_components",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.6",
    install_requires=["streamlit >= 0.63",],
)
