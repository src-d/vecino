import logging
from typing import List, Dict, Any
from uuid import uuid4

from sourced.ml.extractors import IdentifiersBagExtractor
from sourced.ml.models import DocumentFrequencies
from sourced.ml.transformers import Uast2BagFeatures, Ignition, \
    LanguageExtractor, LanguageSelector, UastExtractor, BagFeatures2TermFreq, TFIDF, Collector, \
    HeadFiles, Moder, UastDeserializer, UastRow2Document, RepositoriesFilter
from sourced.ml.utils import create_engine


def repo2bow(repository: str, docfreq_threshold: int, docfreq: DocumentFrequencies,
             languages: List[str] = None, blacklist_languages=False,
             engine_kwargs: Dict[str, Any]=None) -> Dict[str, float]:
    log = logging.getLogger("repo2bow")
    token_index = {"i." + key: int(val) for (key, val) in docfreq}
    session_name = "repo2bow-%s" % uuid4()
    engine_args = {
        "repositories": repository,
        "repository_format": "standard" if not repository.endswith(".git") else "bare",
    }
    if engine_kwargs is not None:
        engine_args.update(engine_kwargs)
    engine = create_engine(session_name, **engine_args)
    root = Ignition(engine) >> RepositoriesFilter(r"^file://.*") >> HeadFiles()
    if languages is not None:
        file_source = root >> \
                      LanguageExtractor() >> \
                      LanguageSelector(languages=languages, blacklist=blacklist_languages)
    else:
        file_source = root
    bag = (file_source >>
           UastExtractor() >>
           Moder("repo") >>
           UastDeserializer() >>
           UastRow2Document() >>
           Uast2BagFeatures(IdentifiersBagExtractor(docfreq_threshold)) >>
           BagFeatures2TermFreq() >>
           TFIDF(token_index, docfreq.docs, engine.session.sparkContext) >>
           Collector()).execute()
    log.info("extracted %d identifiers", len(bag))
    return {r.token[2:]: r.value for r in bag}
