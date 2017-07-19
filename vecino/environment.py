import logging

from modelforge.logs import setup_logging
from ast2vec import ensure_bblfsh_is_running_noexc, install_enry


__initialized__ = False


def initialize(log_level=logging.INFO, enry="./enry"):
    """
    Sets up the working environment: enables logging, launches the Babelfish
    server if it is not running, installs src-d/enry if it is not found in
    PATH.
    :param log_level: The verbosity level. Can be either an integer (e.g. \
    logging.INFO) or a string (e.g. "INFO").
    :param enry: The path to the linguist/enry executable. It if it exists,
    nothing happens. If it is not, src-d/enry is compiled into that file.
    :return:
    """
    global __initialized__
    if __initialized__:
        return
    setup_logging(log_level)
    ensure_bblfsh_is_running_noexc()
    install_enry(target=enry, warn_exists=False)
    __initialized__ = True
