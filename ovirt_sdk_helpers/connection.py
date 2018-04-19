import atexit
import logging

import ovirtsdk4

engine_api_url = "https://fqdn/ovirt-engine/api"
username = "admin@internal"
password = None

# Singleton for connection
con = None

logging.basicConfig(level=logging.DEBUG, filename='base.log')
logger = logging.getLogger(__name__)


def init(url_, username_, password_, insecure=True, **kwargs):
    """
    Create connection to engine

    Args:
        url_ (str): oVirt engine URL
        username_ (str): username@domain to log in
        password_ (str): password for the user to log in
        insecure (bool): use insecure connection only
    """
    global con, engine_api_url, username, password
    engine_api_url = url_
    username = username_
    password = password_

    if con and con.test():
        return

    con = ovirtsdk4.Connection(
        url=engine_api_url,
        username=username,
        password=password,
        insecure=insecure,
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
    global con, engine_api_url, username, password
    if not con or not con.test():
        init(engine_api_url, username, password)
    return con.system_service(*args, **kwargs)


def destroy():
    """
    Destroy connection to engine
    """
    global con
    try:
        con.close()
    except AttributeError:
        pass  # connection was not created
    con = None


atexit.register(destroy)
