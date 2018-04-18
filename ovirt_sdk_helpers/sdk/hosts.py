import ovirt_sdk_helpers as osh

CHECK_UPGRADE_TIMEOUT = 180
CHECK_UPGRADE_SLEEP = 5
HOST_UPGRADE_CHECK_FINISHED = "Check for available updates on host"
HOST_UPGRADE_CHECK_FAILED = "Failed to check for available updates"


def service():
    """
    Get hosts_service object

    Returns:
        obj: hosts_service object
    """
    return osh.connection.system_service().hosts_service()


def get_obj_by_name(host_name, **kwargs):
    """
    Get host object by name

    Args:
        host_name (str): name of the host
        kwargs (dict): keyword arguments for list method

    Returns:
        ovirtsdk4.types.Host: host object
    """
    return service().list(search="name={}".format(host_name), **kwargs)[0]


def get_obj_list(**kwargs):
    """
    Get list of all host objects

    Args:
        kwargs (dict): keyword arguments for list method

    Returns:
        list(obj): list of all host objects
    """
    return service().list(**kwargs)


def host_service(host_name):
    """
    Get host_service for specific host

    Args:
        host_name (str): host name

    Returns:
        obj: host_service object
    """
    host = get_obj_by_name(host_name)
    return service().host_service(host.id)


def is_upgrade_available(host_name):
    """
    Check if upgrade is available for host

    Args:
        host_name (str): name of the host to be upgraded

    Returns:
        bool: True if upgrade is available for host, otherwise False
    """
    return get_obj_by_name(host_name).update_available


def _wait_for_update_check(host_name, last_event_id):
    """
    Wait for update check to finish

    Args:
        host_name (str): host name
        last_event_id (int): id of last event

    Returns:
        bool: True if update check finished successfully, False if update check
        failed, None if event was not found
    """
    for event in osh.events.service().list(
        from_=last_event_id,
        search="host.name={}".format(host_name)
    ):
        if event.description.startswith(HOST_UPGRADE_CHECK_FINISHED):
            return True
        if event.description.startswith(HOST_UPGRADE_CHECK_FAILED):
            return False
    return None


def check_for_upgrade(host_name, wait=False):
    """
    Check for update of packages on host by engine

    Args:
        host_name (str): name of the host to be check upgrade for
        wait (bool): wait for upgrade check to finish

    Returns:
        bool: True if action succeeds otherwise False

    Throws:
        TimeoutExpiredError: when timeout expires, neither succeeded nor
        failed update check message appeared
    """
    host = get_obj_by_name(host_name)

    if not host.update_available:
        host_service(host_name).upgrade_check()

    if wait:
        last_event_id = osh.events.get_latest_id()
        for sample in osh.utils.TimeoutingSampler(
            CHECK_UPGRADE_TIMEOUT, CHECK_UPGRADE_SLEEP, _wait_for_update_check,
            host_name, last_event_id
        ):
            if sample:
                return True
            if not sample and sample is not None:
                return False
    return True


def upgrade(host_name, image=None, async=False, reboot=True, **kwargs):
    """
    Upgrade host

    Ags:
        host_name (str): name of the host to be upgraded
        image (str): image to use in upgrading host (RHEV-H only)
        async (bool): upgrade should be performed asynchronously
        reboot (bool): reboot the host after upgrade

    Returns:
        bool: True if host was upgraded
    """
    host = get_obj_by_name(host_name)

    if host.update_available:
        host_service(host_name).upgrade(
            async=async, image=image, reboot=reboot, **kwargs
        )
    return True
