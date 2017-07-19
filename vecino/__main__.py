import argparse
import logging
import sys

from ast2vec import Id2Vec, DocumentFrequencies, NBOW, Repo2Base
from modelforge.backends import create_backend
from vecino.similar_repositories import SimilarRepositories
from vecino.environment import initialize


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
    parser.add_argument("--nbow", default=None,
                        help="nBOW model URL or path.")
    parser.add_argument("--no-cache-centroids", action="store_true",
                        help="Do not cache WMD centroids.")
    parser.add_argument("--bblfsh", default=None,
                        help="babelfish server address.")
    parser.add_argument(
        "--timeout", type=int, default=Repo2Base.DEFAULT_BBLFSH_TIMEOUT,
        help="Babelfish timeout - longer requests are dropped.")
    parser.add_argument("--gcs", default=None, help="GCS bucket to use.")
    parser.add_argument("--linguist", default=None,
                        help="Path to github/linguist or src-d/enry.")
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
    args = parser.parse_args()
    if args.linguist is None:
        args.linguist = "./enry"
    initialize(args.log_level, enry=args.linguist)
    if args.gcs:
        backend = create_backend(args="bucket=" + args.gcs)
    else:
        backend = create_backend()
    if args.id2vec is not None:
        args.id2vec = Id2Vec(source=args.id2vec, backend=backend)
    if args.df is not None:
        args.df = DocumentFrequencies(source=args.df, backend=backend)
    if args.nbow is not None:
        args.nbow = NBOW(source=args.nbow, backend=backend)
    sr = SimilarRepositories(
        id2vec=args.id2vec, df=args.df, nbow=args.nbow,
        verbosity=args.log_level,
        wmd_cache_centroids=not args.no_cache_centroids,
        gcs_bucket=args.gcs,
        repo2nbow_kwargs={"linguist": args.linguist,
                          "bblfsh_endpoint": args.bblfsh,
                          "timeout": args.timeout},
        wmd_kwargs={"vocabulary_min": args.vocabulary_min,
                    "vocabulary_max": args.vocabulary_max}
    )
    neighbours = sr.query(
        args.input, k=args.nnn, early_stop=args.early_stop,
        max_time=args.max_time, skipped_stop=args.skipped_stop)
    for index, rate in neighbours:
        print("%48s\t%.2f" % (index, rate))


if __name__ == "__main__":
    sys.exit(main())
