import ovirt_sdk_helpers as osh


def wait_for_state(timeout, sleep, state, func, *args, **kwargs):
    """
    Wait for object status

    Args:
        timeout (int): Timeout of sampler
        sleep (int): Time to sleep for between requests
        state (str): Desired state
        func (func): Function to use
        *args (list): Arguments for func
        **kwargs (dict): Keyword arguments for func

    Returns:
        bool: True if desired status was reached, False otherwise
    """
    try:
        for sample in osh.utils.TimeoutingSampler(
            timeout, sleep, func, *args, **kwargs
        ):
            if sample.status == state:
                break
    except osh.utils.TimeoutExpiredError:
        return False
    return True
