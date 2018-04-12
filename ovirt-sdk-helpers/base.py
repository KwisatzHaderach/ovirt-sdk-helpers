import logging

import ovirtsdk4

import config

logging.basicConfig(level=logging.DEBUG, filename='base.log')
logger = logging.getLogger(__name__)


def get_connection(url):
    return ovirtsdk4.Connection(
        url=url,
        username=config.USERNAME,
        password=config.PASSWORD,
        insecure=True,
        debug=True,
        log=logger,
    )
