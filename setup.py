from setuptools import setup, find_packages


setup(
    name="vecino",
    description="Part of source{d}'s stack for machine learning on source "
                "code. Provides API and tools to find similar Git repositories"
                "based on source code identifiers.",
    version="0.1.6-alpha",
    license="Apache 2.0",
    author="source{d}",
    author_email="machine-learning@sourced.tech",
    url="https://github.com/src-d/vecino",
    download_url="https://github.com/src-d/vecino",
    packages=find_packages(exclude=("vecino.tests",)),
    entry_points={
        "console_scripts": ["vecino=vecino.__main__:main"],
    },
    keywords=["machine learning on source code", "word2vec", "id2vec",
              "github", "swivel", "nbow", "bblfsh", "babelfish", "ast2vec"],
    install_requires=["ast2vec>=0.3.8-alpha",
                      "wmd>=1.2.6"],
    package_data={"": ["LICENSE", "README.md"]},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries"
    ]
)
