from setuptools import setup, find_packages


setup(
    name="vecino",
    description="Part of source{d}'s stack for machine learning on source "
                "code. Provides API and tools to find similar GitHub repositories"
                "based on source code identifiers.",
    version="1.0.0",
    license="Apache 2.0",
    author="source{d}",
    author_email="machine-learning@sourced.tech",
    url="https://github.com/src-d/vecino",
    download_url='https://github.com/src-d/vecino',
    packages=find_packages(exclude=("vecino.tests",)),
    keywords=["machine learning on source code", "word2vec", "id2vec",
              "github", "swivel", "nbow", "bblfsh", "babelfish", "ast2vec"],
    install_requires=["ast2vec>-1.0.0",
                      "wmd>=1.2.6"],
    package_data={"": ["LICENSE", "README.md"]},
    classifiers=[
        "Development Status :: 4 - Beta",
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
