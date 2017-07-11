## Vecino

[![Build Status](https://travis-ci.org/src-d/vecino.svg)](https://travis-ci.org/src-d/vecino) [![codecov](https://codecov.io/github/src-d/vecino/coverage.svg?branch=develop)](https://codecov.io/gh/src-d/vecino) [![PyPI](https://img.shields.io/pypi/v/vecino.svg)](https://pypi.python.org/pypi/vecino)

Discovering similar Git repositories.

```python
import vecino

engine = vecino.SimilarRepositories()
print(engine.query("https://github.com/tensorflow/tensorflow"))
```