import atexit
import logging

import ovirtsdk4

from . import config

# Singleton for connection
con = None

logging.basicConfig(level=logging.DEBUG, filename='base.log')
logger = logging.getLogger(__name__)


def init(
    url=config.ENGINE_API_URL,
    username=config.USERNAME,
    password=config.PASSWORD,
    **kwargs
):
    """
    Create connection to engine

    Args:
        url (str): oVirt engine URL
        username (str): username@domain to log in
        password (str): password for the user to log in
    """
    global con
    if con:
        return
    con = ovirtsdk4.Connection(
        url=url,
        username=username,
        password=password,
        insecure=True,
        debug=True,
        log=logger,
        **kwargs
    )


def system_service(*args, **kwargs):
    """
    Get system_service from connection object

    Returns:
        obj: system_service object
    """
    global con
    return con.system_service(*args, **kwargs)


def destroy():
    """
    Destroy connection to engine
    """
    global con
    con.close()
    con = None


atexit.register(destroy)
