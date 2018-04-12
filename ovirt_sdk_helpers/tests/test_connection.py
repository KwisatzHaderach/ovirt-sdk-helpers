from  ovirt_sdk_helpers import connection


class TestConnection:
    def test_basic_connection(self):
        connection.create()
        vms_service = connection._CON.system_service().vms_service()
        for vm in vms_service.list():
            print(vm.name)
