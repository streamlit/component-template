import setuptools

setuptools.setup(
    name="streamlit_carousel",
    version="0.0.1",
    author="Thomas Bouamoud",
    author_email="thomas.bouamoud@gmail.com",
    description="A Streamlit implementation of the React Bootstrap Carousel component.",
    long_description="https://react-bootstrap.netlify.app/docs/components/carousel/",
    long_description_content_type="text/plain",
    url="https://github.com/thomasbs17/streamlit-contributions/bootstrap_carousel",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.6",
    keywords=["python", "streamlit", "react", "bootstrap", "carousel", "gallery"],
    install_requires=["streamlit >= 0.63"],
)
