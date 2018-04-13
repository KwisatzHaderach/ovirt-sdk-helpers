import pytest

from ovirt_sdk_helpers import connection
from ovirt_sdk_helpers.low_level import hosts

HOST_NAME = "host_1"


class TestHostUpgrade:
    @pytest.fixture(scope="class", autouse=True)
    def create_connection(self):
        connection.create()

    def test_upgrade_available(self):
        hosts.is_upgrade_available(HOST_NAME)

    def test_upgrade_check(self):
        assert hosts.check_host_upgrade(HOST_NAME, wait=True)

    def test_host_upgrade(self):
        assert hosts.upgrade_host(HOST_NAME)
