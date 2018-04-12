from ovirt_sdk_helpers import base

from .. import config


class TestConnection:
    def test_basic_connection(self):
        c = base.get_connection(config.ENGINE_API_URL)
        vms_service = c.system_service().vms_service()
        for vm in vms_service.list():
            print(vm.name)
        c.close()
