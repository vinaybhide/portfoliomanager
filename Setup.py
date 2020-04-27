import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Stock-Portfolio-Manager", # Replace with your own username
    version="1.0.1b1",
    author="Vinay Bhide",
    author_email="vinaybhide@hotmail.com",
    description="Portfolio Manager using python, pandas, matplotlib, alpha vantage",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vinaybhide/portfoliomanager",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8.2',
    install_requires=['pandas', 'matplotlib'],
    package_data={"": ["*.csv"],},

)
