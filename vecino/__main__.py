import argparse
import logging
import sys

from sourced.ml.utils import SparkDefault, EngineDefault

from modelforge.backends import create_backend
from modelforge.logs import setup_logging
from sourced.ml.models import Id2Vec, DocumentFrequencies, BOW

from vecino.similar_repositories import SimilarRepositories


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Repository URL or path or name.")
    parser.add_argument("--log-level", default="INFO",
                        choices=logging._nameToLevel,
                        help="Logging verbosity.")
    parser.add_argument("--id2vec", default=None,
                        help="id2vec model URL or path.")
    parser.add_argument("--df", default=None,
                        help="Document frequencies URL or path.")
    parser.add_argument("--bow", default=None,
                        help="BOW model URL or path.")
    parser.add_argument("--prune-df", default=20, type=int,
                        help="Minimum number of times an identifier must occur in the dataset "
                             "to be taken into account.")
    parser.add_argument("--vocabulary-min", default=50, type=int,
                        help="Minimum number of words in a bag.")
    parser.add_argument("--vocabulary-max", default=500, type=int,
                        help="Maximum number of words in a bag.")
    parser.add_argument("-n", "--nnn", default=10, type=int,
                        help="Number of nearest neighbours.")
    parser.add_argument("--early-stop", default=0.1, type=float,
                        help="Maximum fraction of the nBOW dataset to scan.")
    parser.add_argument("--max-time", default=300, type=int,
                        help="Maximum time to spend scanning in seconds.")
    parser.add_argument("--skipped-stop", default=0.95, type=float,
                        help="Minimum fraction of skipped samples to stop.")
    languages = ["Java", "Python", "Go", "JavaScript", "TypeScript", "Ruby", "Bash", "Php"]
    parser.add_argument(
        "-l", "--languages", nargs="+", choices=languages,
        default=None,  # Default value for --languages arg should be None.
        # Otherwise if you process parquet files without 'lang' column, you will
        # fail to process it with any --languages argument.
        help="The programming languages to analyse.")
    parser.add_argument("--blacklist-languages", action="store_true",
                        help="Exclude the languages in --languages from the analysis "
                             "instead of filtering by default.")
    parser.add_argument(
        "-s", "--spark", default=SparkDefault.MASTER_ADDRESS,
        help="Spark's master address.")
    parser.add_argument("--bblfsh", default=EngineDefault.BBLFSH,
                        help="Babelfish server's address.")
    parser.add_argument("--engine", default=EngineDefault.VERSION,
                        help="source{d} jgit-spark-connector version.")
    args = parser.parse_args()
    setup_logging(args.log_level)
    backend = create_backend()
    if args.id2vec is not None:
        args.id2vec = Id2Vec().load(source=args.id2vec, backend=backend)
    if args.df is not None:
        args.df = DocumentFrequencies().load(source=args.df, backend=backend)
    if args.bow is not None:
        args.bow = BOW().load(source=args.bow, backend=backend)
    sr = SimilarRepositories(
        id2vec=args.id2vec, df=args.df, nbow=args.bow,
        prune_df_threshold=args.prune_df,
        wmd_cache_centroids=False,  # useless for a single query
        wmd_kwargs={"vocabulary_min": args.vocabulary_min,
                    "vocabulary_max": args.vocabulary_max},
        languages=(args.languages, args.blacklist_languages),
        engine_kwargs={"spark": args.spark,
                       "bblfsh": args.bblfsh,
                       "engine": args.engine},
    )
    neighbours = sr.query(
        args.input, k=args.nnn, early_stop=args.early_stop,
        max_time=args.max_time, skipped_stop=args.skipped_stop)
    for index, rate in neighbours:
        print("%48s\t%.2f" % (index, rate))


if __name__ == "__main__":
    sys.exit(main())
