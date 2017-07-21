import logging
import re

from ast2vec import Id2Vec, DocumentFrequencies, NBOW, Repo2nBOW
from modelforge.backends import create_backend
from wmd import WMD

from vecino.environment import initialize


class SimilarRepositories:
    GITHUB_URL_RE = re.compile(
        r"(https://|ssh://git@|git://)(github.com/[^/]+/[^/]+)(|.git|/)")

    def __init__(self, id2vec=None, df=None, nbow=None, verbosity=logging.DEBUG,
                 wmd_cache_centroids=True, wmd_kwargs=None, gcs_bucket=None,
                 repo2nbow_kwargs=None, initialize_environment=True):
        if initialize_environment:
            initialize()
        self._log = logging.getLogger("similar_repos")
        self._log.setLevel(verbosity)
        if gcs_bucket:
            backend = create_backend(args="bucket=" + gcs_bucket)
        else:
            backend = create_backend()
        if id2vec is None:
            self._id2vec = Id2Vec(log_level=verbosity, backend=backend)
        else:
            assert isinstance(id2vec, Id2Vec)
            self._id2vec = id2vec
        self._log.info("Loaded id2vec model: %s", self._id2vec)
        if df is None:
            if df is not False:
                self._df = DocumentFrequencies(log_level=verbosity, backend=backend)
            else:
                self._df = None
                self._log.warning("Disabled document frequencies - you will "
                                  "not be able to query custom repositories.")
        else:
            assert isinstance(df, DocumentFrequencies)
            self._df = df
        self._log.info("Loaded document frequencies: %s", self._df)
        if nbow is None:
            self._nbow = NBOW(log_level=verbosity, backend=backend)
        else:
            assert isinstance(nbow, NBOW)
            self._nbow = nbow
        self._log.info("Loaded nBOW model: %s", self._nbow)
        self._repo2nbow = Repo2nBOW(
            self._id2vec, self._df, log_level=verbosity, **(repo2nbow_kwargs or {}))
        self._log.info("Creating the WMD engine...")
        self._wmd = WMD(self._id2vec.embeddings, self._nbow,
                        verbosity=verbosity, **(wmd_kwargs or {}))
        if wmd_cache_centroids:
            self._wmd.cache_centroids()

    def query(self, url_or_path_or_name, **kwargs):
        try:
            repo_index = self._nbow.repository_index_by_name(
                url_or_path_or_name)
        except KeyError:
            repo_index = -1
        if repo_index == -1:
            match = self.GITHUB_URL_RE.match(url_or_path_or_name)
            if match is not None:
                name = match.group(2)
                try:
                    repo_index = self._nbow.repository_index_by_name(name)
                except KeyError:
                    pass
        if repo_index >= 0:
            neighbours = self._query_domestic(repo_index, **kwargs)
        else:
            neighbours = self._query_foreign(url_or_path_or_name, **kwargs)
        neighbours = [(self._nbow[n[0]][0], n[1]) for n in neighbours]
        return neighbours

    @staticmethod
    def unicorn_query(repo_name, id2vec=None, nbow=None, wmd_kwargs=None,
                      query_wmd_kwargs=None):
        sr = SimilarRepositories(
            id2vec=id2vec, df=False, nbow=nbow,
            wmd_kwargs=wmd_kwargs or {
                "vocabulary_min": 50,
                "vocabulary_max": 500
            }
        )
        return sr.query(
            repo_name, **(query_wmd_kwargs or {
                "early_stop": 0.1, "max_time": 180, "skipped_stop": 0.95}))

    def _query_domestic(self, repo_index, **kwargs):
        return self._wmd.nearest_neighbors(repo_index, **kwargs)

    def _query_foreign(self, url_or_path, **kwargs):
        if self._df is None:
            raise ValueError("Cannot query custom repositories if the "
                             "document frequencies are disabled.")
        nbow_dict = self._repo2nbow.convert_repository(url_or_path)
        words = sorted(nbow_dict.keys())
        weights = [nbow_dict[k] for k in words]
        return self._wmd.nearest_neighbors((words, weights), **kwargs)
