from pathlib import Path

import setuptools

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    name="streamlit-keyup",
    version="0.1.7",
    author="Zachary Blackwood",
    author_email="zachary@streamlit.io",
    description="Text input that renders on keyup",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/blackary/streamlit-keyup",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.7",
    install_requires=["streamlit>=1.2", "jinja2"],
)
