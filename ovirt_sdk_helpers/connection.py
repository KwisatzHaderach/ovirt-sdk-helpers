import atexit
import logging

import ovirtsdk4

# Singleton for connection
con = None

logging.basicConfig(
    level=logging.DEBUG, filename='ovirt_sdk_helper.log'
)
logger = logging.getLogger(__name__)

con_params = {
    'url': "https://fqdn/ovirt-engine/api",
    'username': "admin@internal",
    'password': None,
    'insecure': False,
    'debug': True,
    'log': logger
}


def init(url, username, password, **kwargs):
    """
    Create connection to engine

    Args:
        url (str): oVirt engine URL
        username (str): username@domain to log in
        password (str): password for the user to log in

    Kwargs:
        http://ovirt.github.io/ovirt-engine-sdk/master/#ovirtsdk4.Connection.__init__
    """
    global con, con_params
    con_params['url'] = url
    con_params['username'] = username
    con_params['password'] = password
    con_params.update(kwargs)

    if con and con.test():
        return

    con = ovirtsdk4.Connection(**con_params)


def system_service(*args, **kwargs):
    """
    Get system_service from connection object

    Returns:
        obj: system_service object
    """
    global con, con_params
    if not con or not con.test():
        init(**con_params)
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
