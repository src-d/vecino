import logging
import os
import re
import sys
import tempfile
from typing import Dict, Any, List, Tuple

from dulwich import porcelain
from modelforge.backends import create_backend
from sourced.ml.models import Id2Vec, DocumentFrequencies, BOW
from wmd import WMD

from vecino.repo2bow import repo2bow


class SimilarRepositories:
    GITHUB_URL_RE = re.compile(
        r"(https://|ssh://git@|git://)(github.com/[^/]+/[^/]+)(|.git|/)")
    _log = logging.getLogger("SimilarRepositories")

    def __init__(self, id2vec=None, df=None, nbow=None, prune_df_threshold=1,
                 wmd_cache_centroids=True, wmd_kwargs: Dict[str, Any] = None,
                 languages: Tuple[List, bool] = (None, False),
                 engine_kwargs: Dict[str, Any] = None):
        backend = create_backend()
        if id2vec is None:
            self._id2vec = Id2Vec().load(backend=backend)
        else:
            assert isinstance(id2vec, Id2Vec)
            self._id2vec = id2vec
        self._log.info("Loaded id2vec model: %s", self._id2vec)
        if df is None:
            if df is not False:
                self._df = DocumentFrequencies().load(backend=backend)
            else:
                self._df = None
                self._log.warning("Disabled document frequencies - you will "
                                  "not be able to query custom repositories.")
        else:
            assert isinstance(df, DocumentFrequencies)
            self._df = df
        if self._df is not None:
            self._df = self._df.prune(prune_df_threshold)
        self._log.info("Loaded document frequencies: %s", self._df)
        if nbow is None:
            self._bow = BOW().load(backend=backend)
        else:
            assert isinstance(nbow, BOW)
            self._bow = nbow
        self._log.info("Loaded BOW model: %s", self._bow)
        assert self._bow.get_dep("id2vec")["uuid"] == self._id2vec.meta["uuid"]
        if len(self._id2vec) != self._bow.matrix.shape[1]:
            raise ValueError("Models do not match: id2vec has %s tokens while nbow has %s" %
                             (len(self._id2vec), self._bow.matrix.shape[1]))
        self._log.info("Creating the WMD engine...")
        self._wmd = WMD(self._id2vec.embeddings, self._bow, **(wmd_kwargs or {}))
        if wmd_cache_centroids:
            self._wmd.cache_centroids()
        self._languages = languages
        self._engine_kwargs = engine_kwargs

    def query(self, url_or_path_or_name: str, **kwargs) -> List[Tuple[str, float]]:
        try:
            repo_index = self._bow.documents.index(url_or_path_or_name)
        except ValueError:
            repo_index = -1
        if repo_index == -1:
            match = self.GITHUB_URL_RE.match(url_or_path_or_name)
            if match is not None:
                name = match.group(2)
                try:
                    repo_index = self._bow.repository_index_by_name(name)
                except KeyError:
                    pass
        if repo_index >= 0:
            neighbours = self._query_domestic(repo_index, **kwargs)
        else:
            neighbours = self._query_foreign(url_or_path_or_name, **kwargs)
        neighbours = [(self._bow[n[0]][0], n[1]) for n in neighbours]
        return neighbours

    def _query_domestic(self, repo_index, **kwargs):
        return self._wmd.nearest_neighbors(repo_index, **kwargs)

    def _query_foreign(self, url_or_path: str, **kwargs):
        df = self._df
        if df is None:
            raise ValueError("Cannot query custom repositories if the "
                             "document frequencies are disabled.")

        with tempfile.TemporaryDirectory(prefix="vecino-") as tempdir:
            target = os.path.join(tempdir, "repo")
            if os.path.isdir(url_or_path):
                url_or_path = os.path.abspath(url_or_path)
                os.symlink(url_or_path, target, target_is_directory=True)
            else:
                porcelain.clone(url_or_path, target, bare=True, outstream=sys.stderr)
            bow = repo2bow(tempdir, 1, df, *self._languages, engine_kwargs=self._engine_kwargs)
        ibow = {}
        for key, val in bow.items():
            try:
                ibow[self._id2vec[key]] = val
            except KeyError:
                continue
        words, weights = zip(*sorted(ibow.items()))
        return self._wmd.nearest_neighbors((words, weights), **kwargs)
