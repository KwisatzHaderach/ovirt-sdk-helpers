import ovirt_sdk_helpers as osh


def service():
    """
    Get events_service object

    Returns:
        obj: events_service object
    """
    return osh.connection.system_service().events_service()


def get_latest_id():
    """
    Get ID of latest event

    Returns:
        int: last event id
    """
    return int(service().list(max=1)[0].id)
