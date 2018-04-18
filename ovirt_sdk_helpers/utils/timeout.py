import time
import logging

logger = logging.getLogger(__name__)


class TimeoutExpiredError(Exception):
    message = 'Timed Out'

    def __init__(self, *value):
        self.value = value

    def __str__(self):
        return "%s: %s" % (self.message, repr(self.value))


class TimeoutingSampler(object):
    """
    Samples the function output.

    This is a generator object that at first yields the output of function
    `func`. After the yield, it either raises instance of `timeout_exc_cls` or
    sleeps `sleep` seconds.

    Yielding the output allows you to handle every value as you wish.
    """

    def __init__(self, timeout, sleep, func, *func_args, **func_kwargs):
        """
        See the doc for TimeoutingSampler.

        Args:
            timeout (int): max time to wait
            sleep (int): sleep between checks
            func (func): function to execute
            *func_args (list): non keyword arguments for function
            **func_kwargs (dict): keyword arguments for function
        """

        self.timeout = timeout
        self.sleep = sleep
        self.func = func
        self.func_args = func_args
        self.func_kwargs = func_kwargs

        self.start_time = None
        self.last_sample_time = None

        self.timeout_exc_cls = TimeoutExpiredError
        """ Class of exception to be raised. """
        self.timeout_exc_args = (self.timeout,)
        """ An args for __init__ of the timeout exception. """
        self.timeout_exc_kwargs = {}
        """ A kwargs for __init__ of the timeout exception. """

    def __iter__(self):
        if self.start_time is None:
            self.start_time = time.time()
        while True:
            self.last_sample_time = time.time()
            yield self.func(*self.func_args, **self.func_kwargs)
            if self.timeout < (time.time() - self.start_time):
                raise self.timeout_exc_cls(
                    *self.timeout_exc_args, **self.timeout_exc_kwargs
                )
            time.sleep(self.sleep)
