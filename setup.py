import os

from setuptools import setup, find_packages

module_dir = os.path.dirname(os.path.abspath(__file__))

setup(
    name="decampy",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    url="https://github.com/dwinston/decampy",
    license="MIT",
    author="Donny Winston",
    author_email="dwinston@lbl.gov",
    description="Converts DataCamp repos to the format of https://github.com/ines/course-starter-python",
    long_description=open(os.path.join(module_dir, "README.md")).read(),
    long_description_content_type="text/markdown",
    install_requires=[],
    extras_require={"dev": ["black", "invoke", "pre-commit", "twine"]},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Topic :: Education",
        "Topic :: Education :: Computer Aided Instruction (CAI)",
        "Topic :: Text Processing :: Markup",
    ],
    keywords="datacamp python online-course jupyter binder",
    python_requires=">=3.7",
    entry_points={"console_scripts": ["decampy=decampy.cli:main"]},
)
