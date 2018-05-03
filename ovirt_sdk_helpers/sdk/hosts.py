import ovirtsdk4

import ovirt_sdk_helpers as osh

HOST_TIMEOUT = 600
HOST_SLEEP = 10
CHECK_UPGRADE_TIMEOUT = 180
CHECK_UPGRADE_SLEEP = 5
HOST_INSTALL_TIMEOUT = 800
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
    try:
        return service().list(search="name={}".format(host_name), **kwargs)[0]
    except IndexError:
        return None


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


def wait_for_hosts_states(
    names, state=ovirtsdk4.types.HostStatus.UP,
    timeout=HOST_TIMEOUT, sleep=HOST_SLEEP
):
    """
    Wait until all of the hosts identified by names exist and have the desired
    status declared in states.

    Args:
        names (str or list): A comma separated names (or a list) of the hosts
        state (str): A state of the hosts to wait for
        timeout (int): Timeout for sampler
        sleep (int): Time to sleep between host status queries

    Returns:
        bool: True if hosts are in states, False otherwise.
    """
    if isinstance(names, str):
        names = names.split(",")
    for host in names:
        if not osh.general.wait_for_state(
            timeout, sleep, state, get_obj_by_name, host
        ):
            return False
    return True


def add(
    name, address, root_password, cluster, wait=True,
    deploy_hosted_engine=False, **kwargs
):
    """
    Add new host

    Args:
        name (str): Host name
        address (str): Host FQDN or IP
        root_password (str): Host root password
        cluster (str): Host cluster name
        wait (bool): Wait until the host will have state UP
        deploy_hosted_engine (bool): Deploy hosted engine flag

    Keyword Args:
        http://ovirt.github.io/ovirt-engine-sdk/master/types.m.html#ovirtsdk4.types.Host

    Returns:
        bool: True, if add action succeeds, otherwise False
    """
    service().add(
        ovirtsdk4.types.Host(
            name=name, address=address, root_password=root_password,
            cluster=ovirtsdk4.types.Cluster(name=cluster), **kwargs
        ),
        deploy_hosted_engine=deploy_hosted_engine
    )

    if wait:
        return wait_for_hosts_states(name, timeout=HOST_INSTALL_TIMEOUT)
    return True


def update(name_, **kwargs):
    """
    Update properties of a host

    Args:
        name_ (str): Name of a target host

    Keyword Arguments:
        http://ovirt.github.io/ovirt-engine-sdk/master/types.m.html#ovirtsdk4.types.Host
    """
    host_service(name_).update(ovirtsdk4.types.Host(**kwargs))


def remove(name, deactivate=False):
    """
    Remove existing host

    Args:
        name (str): Name of a host to be removed
        deactivate (bool): Flag to put host in maintenance before remove

    Returns:
        bool: If the host was removed correctly
    """
    _host_service = host_service(name)
    if deactivate:
        _host_service.deactivate()
        if not wait_for_hosts_states(
            name, state=ovirtsdk4.types.HostStatus.MAINTENANCE
        ):
            return False

    _host_service.remove()
    if get_obj_by_name(name):
        return False
    return True


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


def upgrade(
    host_name, image=None, async=False, reboot=True, **kwargs  # noqa: W606
):
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
            async=async, image=image, reboot=reboot, **kwargs  # noqa: W606
        )
    return True
