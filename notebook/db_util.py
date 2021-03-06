# Db util class which take care of executing queries.

import os

import django
from django.conf import settings


from deming import deming_setup

# PG values.
PG_DB_USER = os.environ.get('PG_DB_USER', '')
PG_DB_NAME = os.environ.get('PG_DB_NAME', '')
PG_DB_PASS = os.environ.get('PG_DB_PASS', '')
PG_DB_HOST = os.environ.get('PG_DB_HOST', '')
PG_DB_PORT = os.environ.get('PG_DB_PORT', '')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': PG_DB_NAME,
        'USER': PG_DB_USER,
        'PASSWORD': PG_DB_PASS,
        'HOST': PG_DB_HOST,
        'PORT': PG_DB_PORT,
    }
}

settings.configure(
    DATABASES=DATABASES,
    SECRET_KEY='1234578',
    LANGUAGE_CODE='en-us',
    TIME_ZONE='UTC',
    USE_I18N=True,
    USE_L10N=True,
    USE_TZ=True,
    INSTALLED_APPS=[
        'deming_core',
        'django.contrib.auth',
        'django.contrib.admin',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
    ])

django.setup()

from deming.models import EnterpriseUser, KernelSession, EdgeDevice
from deming.edge import device_types
from deming.edge.status import ACTIVE

class ExecuteQueries:
    """
    This class contains all the helper methods for executing queries using django orms.
    The logic of  django orm is kept here so that we don't repeat the imports and setup django in different files.
    """

    def get_active_devices(self, edge_devices):
        """
        Get active devices
        :param edge_devices: edge device query set.
        :return: list of active edge devices.
        """

        return [edge_device for edge_device in edge_devices if edge_device.status == ACTIVE]

    def get_mlnodes(self):
        """
        Get all the mlnode instances that are present in the MLNode table.
        :return: List of Mlnode instances.
        """

        return self.get_active_devices(EdgeDevice.objects.filter(device_type__in=device_types.valid_ml_node_types,
                                                                 system_status__is_connected=True))

    def get_ml_node(self, column_name, column_value):
        """
        Get ml node instances for the given column name and value.
        :param column_name: (str) Name of the column.
        :param column_value: (str) Value of column.
        :return: List of Mlnode instances.
        """
        kwargs = {column_name: column_value}
        return self.get_active_devices(EdgeDevice.objects.filter(device_type__in=device_types.valid_ml_node_types,
                                                                 system_status__is_connected=True).filter(**kwargs))

    def delete_kernel_session(self, column_name, column_value):
        """
        Delete the entry in the Kernel Session table for the given column name and Value.
        :param column_name: (str) Name of the column
        :param column_value: (str) Value of column
        :return: List of KernelSession instances.
        """
        kwargs = {column_name: column_value}
        return KernelSession.objects.filter(**kwargs).delete()

    def get_kernel_session(self, column_name, column_value):
        """
        Get kernel session instances for the given column name and value.
        :param column_name: (str) Name of the column
        :param column_value: (str) Value of column
        :return: List of KernelSession instances.
        """
        kwargs = {column_name: column_value}
        return KernelSession.objects.filter(**kwargs)

    def create_kernel_session(self, _field_values):
        """
        Create kernel session instance with provided values.
        :param _field_values: (Dict) Dictionary of field values.
        :return: KernelSession instance.
        """

        _kernel_id = _field_values.get("kernel_id", None)
        _kernel_name = _field_values.get("kernel_name", None)
        mlnode_id = _field_values['mlnode_id']
        result, _ = KernelSession.objects.update_or_create(kernel_id=_kernel_id,
                                                           kernel_name=_kernel_name,
                                                           ml_node=EdgeDevice.objects.get(id=mlnode_id))
        return result

    def check_kernel_sessions(self, column_name, column_value):
        """
        Check if there is an entry wih the following field and value.
        :param column_name: Name of the Column. ( String )
        :param column_value: Value of the Column. ( String )
        :return: Boolean Value.
        """

        kwargs = {column_name: column_value}
        return KernelSession.objects.filter(**kwargs).exists()

    def update_kernel_session(self, _field_values):
        """
        Update the kernel session values.
        :param _field_values: (Dict) Dictionary of field values.
        """
        try:
            kernel_session = KernelSession.objects.get(
                kernel_id=_field_values['kernel_id'])

            if 'user_name' in _field_values.keys():
                user = EnterpriseUser.objects.get(
                    username=_field_values['user_name'])
                kernel_session.enterprise_user = user

            kernel_session.save()

        except Exception as e:
            print(f'Error occurred in updating kernel session ={e}')

    def get_mlnode_address(self):
        """
        Get address for all the mlnodes
        :return: List of address for Mlnodes instances.
        """
        mlnodes = self.get_active_devices(EdgeDevice.objects.filter(device_type__in=device_types.valid_ml_node_types,
                                                                    system_status__is_connected=True))
        return [f'https://{str(mlnode.ip_address)}' for mlnode in mlnodes]

    def get_mlnode_address_with_field(self, column_name, column_value):
        """
        Get ml node instances for the given column name and value. Provided a field value.
        :param column_name: Name of the Column. ( String )
        :param column_value: Value of the Column. ( String )
        :return: Address for Mlnode instances.
        """
        kwargs = {column_name: column_value}
        mlnode = EdgeDevice.objects.get(**kwargs)
        return f'https://{str(mlnode.ip_address)}'
