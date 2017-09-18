## Vecino

[![Build Status](https://travis-ci.org/src-d/vecino.svg)](https://travis-ci.org/src-d/vecino) [![codecov](https://codecov.io/github/src-d/vecino/coverage.svg?branch=master)](https://codecov.io/gh/src-d/vecino) [![PyPI](https://img.shields.io/pypi/v/vecino.svg)](https://pypi.python.org/pypi/vecino)

Discovering similar Git repositories.

```python
import vecino

engine = vecino.SimilarRepositories()
print(engine.query("https://github.com/tensorflow/tensorflow"))
```

### Docker image

```
docker build -t srcd/vecino .
docker run -d --privileged -p 9432:9432 --name bblfsh --rm bblfsh/server
docker run -it --rm srcd/vecino https://github.com/apache/spark
```

In order to cache the downloaded models:

```
docker run -it --rm -v /path/to/cache/on/host:/root srcd/vecino https://github.com/apache/spark
```