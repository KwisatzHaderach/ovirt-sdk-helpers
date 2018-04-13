from time import sleep

from ovirt_sdk_helpers import connection

CHECK_UPGRADE_TIMEOUT = 180
CHECK_UPGRADE_SLEEP = 5
HOST_UPGRADE_CHECK_FINISHED = "Check for available updates on host"
HOST_UPGRADE_CHECK_FAILED = "Failed to check for available updates"


def get_host_by_name(host_name):
    """
    Get host object by name

    Args:
        host_name (str): name of the host

    Returns:
        ovirtsdk4.types.Host: host object
    """
    hosts_service = connection._CON.system_service().hosts_service()
    return hosts_service.list(search="name={}".format(host_name))[0]


def is_upgrade_available(host_name):
    """
    Check if upgrade is available for host

    Args:
        host_name (str): name of the host to be upgraded

    Returns:
        bool: True if upgrade is available for host, otherwise False
    """
    return get_host_by_name(host_name).update_available


def check_host_upgrade(host_name, wait=False):
    """
    Check for update of packages on host by engine

    Args:
        host_name (str): name of the host to be check upgrade for
        wait (bool): wait for upgrade check to finish

    Returns:
        bool: True if action succeeds otherwise False
    """
    host = get_host_by_name(host_name)
    host_service = (
        connection._CON.system_service().hosts_service().host_service(host.id)
    )

    if not host.update_available:
        host_service.upgrade_check()

    timeout = 0
    if wait:
        events_service = connection._CON.system_service().events_service()
        last_event = events_service.list(max=1)[0]
        while timeout < CHECK_UPGRADE_TIMEOUT:
            for event in events_service.list(
                from_=int(last_event.id),
                search="host.name={}".format(host.name)
            ):
                if event.description.startswith(HOST_UPGRADE_CHECK_FINISHED):
                    return True
                if event.description.startswith(HOST_UPGRADE_CHECK_FAILED):
                    return False
            timeout += CHECK_UPGRADE_SLEEP
            sleep(CHECK_UPGRADE_SLEEP)
        return False
    return True


def upgrade_host(host_name, image=None, async=False, reboot=True):
    """
    Upgrade host

    Ags:
        host_name (str): name of the host to be upgraded
        image (str): image to use in upgrading host (RHEV-H only)
        async (bool): upgrade should be performed asynchronously
        reboot (bool): reboot the host after upgrade

    Returns:
        bool: True if host was upgraded, otherwise False
    """
    host = get_host_by_name(host_name)
    host_service = (
        connection._CON.system_service().hosts_service().host_service(host.id)
    )

    if host.update_available:
        host_service.upgrade(async=async, image=image, reboot=reboot)
    return True
