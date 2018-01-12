# Vecino [![Build Status](https://travis-ci.org/src-d/vecino.svg)](https://travis-ci.org/src-d/vecino) [![codecov](https://codecov.io/github/src-d/vecino/coverage.svg?branch=master)](https://codecov.io/gh/src-d/vecino) [![PyPI](https://img.shields.io/pypi/v/vecino.svg)](https://pypi.python.org/pypi/vecino)

Vecino is a command line application to discover Git repositories which are similar
to the one that the user provides.

```
$ vecino https://github.com/apache/spark
...
                                    apache/spark	4.07
                                   amplab/graphx	5.80
                               EclairJS/eclairjs	5.84
                       EclairJS/eclairjs-nashorn	5.87
                                 cloudera/impyla	6.01
                           databricks/spark-perf	6.26
                                forward3d/rbhive	6.29
                                     apache/hive	6.29
                              ondra-m/ruby-spark	6.31
                        SnappyDataInc/snappydata	6.31
```

Finding related open source software can be hard. Sometimes using a search engine is not enough.
One of the reliable ways to determine projects which seem to be close to yours is to look into
the source code and let it judge. Vecino defines similarity through matching or synonymical
source code identifiers.

Vecino uses id2vec, source{d}'s source code identifer embeddings and much of
[ast2vec](https://github.com/src-d/ast2vec) engine. Parsing is performed with [Babelfish](http://doc.bblf.sh).
The suggested repositories are taken from the loaded NBOW model - the only currently available now
is from October 2016.

### Please note

The currently available public models were converted and are outdated and not fully compatible with
the preprocessing in ast2vec. Thus the results can be imprecise. The original results can be reproduced in
the [reference notebook](reference/nearest_repos.ipynb).

Besides, since Babelfish supports only Python and Java at the moment, it is impossible to query
repositories written in other languages.

### Installation

```
pip3 install vecino
```

As in the rest of ML projects at source{d}, only Python3 is supported and Python2 will never be.

### Usage

Command line:

```
$ vecino apache/spark
```

Python API:

```python
import vecino

engine = vecino.SimilarRepositories()
print(engine.query("https://github.com/apache/spark"))
```

### Docker image

```
docker build -t srcd/vecino .
docker run -d --privileged -p 9432:9432 --name bblfshd bblfsh/bblfshd
docker exec -it bblfshd bblfshctl driver install --all
docker run -it --rm srcd/vecino https://github.com/apache/spark
```

In order to cache the downloaded models:

```
docker run -it --rm -v /path/to/cache/on/host:/root srcd/vecino https://github.com/apache/spark
```

### Contributions

...are welcome! See [CONTRIBUTING](CONTRIBUTING.md) and [code of conduct](CODE_OF_CONDUCT.md).

### License

[Apache 2.0](LICENSE.md)
