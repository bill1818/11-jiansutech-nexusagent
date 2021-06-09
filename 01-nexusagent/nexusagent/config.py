import os
import yaml
import logging
import requests


def manager_config(path):
    '''
    Reads in the master configuration file and sets up default options
    '''
    opts = {'conf_file': path,
            'session': requests.Session()}

    if os.path.isfile(path):
        try:
            opts.update(yaml.load(open(path, 'r')))
        except Exception:
            pass

    logging.getLogger("requests").setLevel(logging.WARNING)
    opts['logger'] = manager_logger(opts['log_file'],
                                    opts['log_level'])

    return opts


def manager_logger(log_file, log_level):
    '''
    Returns a logger fo use with a serviceagent master
    '''
    if not os.path.isdir(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file))

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    fh_ = logging.FileHandler(log_file)
    fh_.setLevel(getattr(logging, log_level))

    fmt = '%(asctime)s - %(name)s - %(levelname)s - nagent[%(process)d]: %(message)s'
    formatter = logging.Formatter(fmt)
    fh_.setFormatter(formatter)
    logger.addHandler(fh_)

    return logger
