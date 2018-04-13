import atexit
import logging

import ovirtsdk4

from . import config

_CON = None

logging.basicConfig(level=logging.DEBUG, filename='base.log')
logger = logging.getLogger(__name__)


def create(
    url=config.ENGINE_API_URL,
    username=config.USERNAME,
    password=config.PASSWORD
):
    """
    Create a connection

    Args:
        url (str): ovirt engine url
        username (str): username@domain to log in
        password (str): password for the user to log in
    """
    global _CON
    if _CON:
        return
    _CON = ovirtsdk4.Connection(
        url=url,
        username=username,
        password=password,
        insecure=True,
        debug=True,
        log=logger,
    )


def destroy():
    global _CON
    _CON.close()


atexit.register(destroy)
