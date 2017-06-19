## Vecino

Discovering similar Git repositories.

```python
import vecino

engine = vecino.SimilarRepositories()
print(engine.query("https://github.com/tensorflow/tensorflow"))
```