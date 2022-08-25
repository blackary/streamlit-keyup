import setuptools

setuptools.setup(
    name="streamlit-keyup",
    version="0.1.1",
    author="Zachary Blackwood",
    author_email="zachary@streamlit.io",
    description="Text input that renders on keyup",
    long_description="",
    long_description_content_type="text/plain",
    url="https://github.com/blackary/streamlit-keyup",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.7",
    install_requires=["streamlit>=1.2", "jinja2"],
)
