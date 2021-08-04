# Db util class which take care of executing queries.

import os
import requests
from requests.auth import HTTPBasicAuth

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

HOST = "localhost"
PORT = 8000

API = f'http://{HOST}:{PORT}/qnnect/ml_node/'
API_KERNEL = f'http://{HOST}:{PORT}/qnnect/kernel_session/'
print("API IS", API)


class ExecuteQueries:
    """
    This class contains all the helper methods for executing queries using django orms.
    The logic of  django orm is kept here so that we don't repeat the imports and setup django in different files.
    """

    def get_active_devices(self, edge_devices: list[dict]) -> list[dict]:
        """
        Get active devices
        :param edge_devices: List of dictionaries (the JSON response from API)
        :return: list of active edge devices.
        """

        return [edge_device for edge_device in edge_devices]

    def get_mlnodes(self):
        """
        Get all the mlnode instances that are present in the MLNode table.
        :return: List of Mlnode instances.
        """
        resp = requests.get(API, auth=HTTPBasicAuth(USERNAME, PASSWORD))
        ml_nodes_json = resp.json()
        return self.get_active_devices(ml_nodes_json)

    def get_ml_node(self, column_name: str, column_value: str) -> dict:
        """
        Get the first instance of MLNode which matches the given column name and value.
        :param column_name: (str) Name of the column.
        :param column_value: (str) Value of column.
        :return: A single MLNode instance
        """
        ml_nodes = self.get_mlnodes()
        print("get_ml_nodes ====", ml_nodes)
        return list(filter(lambda ml_node: ml_node[column_name] == column_value, ml_nodes))[0]
    
    
    def delete_kernel_session(self, kernel_id: str) -> dict:
        """
        Delete the entry in the Kernel Session table for the given `kernel_id`
        :param kernel_id: (str) UUID of the KernelSession which is to be deleted
        :return: List of KernelSession instances.
        """
        print("deleting kernel session")
        resp = requests.delete(API_KERNEL, params={"kernel_id": kernel_id})
        return resp.json()

    def get_kernel_session(self, column_name: str, column_value: str) -> dict:
        """
        Get the first instance of kernel session which matches the given column name and value.
        :param column_name: (str) Name of the column
        :param column_value: (str) Value of column
        :return: A single KernelSession instance
        """
        print("getting kernel session")
        kwargs = {column_name: column_value}
        resp = requests.get(API_KERNEL, params=kwargs, auth=HTTPBasicAuth(USERNAME, PASSWORD))
        resp_json = resp.json()
        print(resp_json, "is the response")
        return resp_json[0]

    def create_kernel_session(self, _field_values: dict) -> dict:
        """
        Create kernel session instance with provided values.
        :param _field_values: (Dict) Dictionary of field values.
        :return: JSON serialized KernelSession instance.
        """
        print("Creating a KernelSession")
        _kernel_id = _field_values.get("kernel_id")
        _kernel_name = _field_values.get("kernel_name")
        mlnode_id = _field_values['mlnode_id']
        data={
            "kernel_id": _kernel_id,
            "kernel_name": _kernel_name,
            "ml_node": int(mlnode_id),
        }
        print("data", data)
        resp = requests.post(API_KERNEL, data=data, auth=HTTPBasicAuth(USERNAME, PASSWORD))
        resp_json = resp.json()
        print(resp_json)
        return resp_json

    def check_kernel_sessions(self, column_name: str, column_value: str) -> bool:
        """
        Check if there is an entry wih the following field and value.
        :param column_name: Name of the Column. ( String )
        :param column_value: Value of the Column. ( String )
        :return: Boolean Value.
        """
        print("checking if exists kernel session")

        raise NotImplementedError

    def update_kernel_session(self, _field_values):
        """
        Update the kernel session values.
        :param _field_values: (Dict) Dictionary of field values.
        """
        print("updating kernel session")
        try:
            print(42)
            # kernel_session = KernelSession.objects.get(
            #     kernel_id=_field_values['kernel_id'])

            # if 'user_name' in _field_values.keys():
            #     user = EnterpriseUser.objects.get(
            #         username=_field_values['user_name'])
            #     kernel_session.enterprise_user = user

            # kernel_session.save()

        except Exception as e:
            print(f'Error occurred in updating kernel session ={e}')
        # raise NotImplementedError

    def get_mlnode_address(self) -> list[str]:
        """
        Get address for all the mlnodes
        :return: List of address for Mlnodes instances.
        """
        mlnodes = self.get_mlnodes()
        return [f"https://{mlnode['ip_address']}" for mlnode in mlnodes]

    def get_mlnode_address_with_field(self, column_name: str, column_value: str) -> str:
        """
        Get ml node instances for the given column name and value. Provided a field value.
        :param column_name: Name of the Column. ( String )
        :param column_value: Value of the Column. ( String )
        :return: Address for Mlnode instances.
        """
        print(f"{column_name=} {column_value=}")
        mlnode = self.get_ml_node(column_name, int(column_value))
        return f"https://{mlnode['ip_address']}"
