import requests, logging
from requests.auth import HTTPBasicAuth
from connectors.core.connector import get_logger, ConnectorError
from .constants import *
from requests_toolbelt.utils import dump

logger = get_logger('juniper_junos')
logger.setLevel(logging.DEBUG) #Disable for prod

# Globals/Endpoints



def _get_input(params, key, type):
    ret_val = params.get(key, None)
    if ret_val:
        if isinstance(ret_val, bytes):
            ret_val = ret_val.decode('utf-8')
        if isinstance(ret_val, type):
            return ret_val
        else:
            logger.info(
                'Parameter Input Type is Invalid: Parameter is: {0}, Required Parameter Type is: {1}'.format(
                    str(key), str(type)))
            raise ConnectorError(
                'Parameter Input Type is Invalid: Parameter is: {0}, Required Parameter Type is: {1}'.format(str(key),
                                                                                                             str(type)))
    else:
        if ret_val == {} or ret_val == [] or ret_val == 0:
            return ret_val
        return None


def _get_config(config):
    device_url = config.get('device_url')[:-1] if config.get('device_url')[-1] == '/' else config.get('device_url')
    tcp_port = config.get('tcp_port')
    username = config.get('username')
    password = config.get('password')
    verify_ssl = config.get('verify_ssl')    
    if device_url[:7] != 'http://' and device_url[:8] != 'https://':
        device_url = 'https://{}'.format(device_url)
    return device_url, tcp_port, username, password, verify_ssl


def _api_request(method, endpoint, config, payload={}, header={'Accept':'application/json'}, params={}):
    try:
        device_url, tcp_port, username, password, verify_ssl = _get_config(config)
        url = JUNOS_URL.format(device_url,tcp_port,endpoint)

        api_response = requests.request(method=method, url=url, auth=HTTPBasicAuth(username, password), headers=header, params=params, data=payload, verify=verify_ssl)
        logger.debug('REQUESTS_DUMP:\n{}'.format(dump.dump_all(api_response).decode('utf-8')))                                        
        if api_response.ok:
            return api_response.content.decode('utf-8')
        else:
            logger.info('Fail To request API {0} response is : {1}'.format(str(url), str(api_response.content)))
            raise ConnectorError('Fail To request API {0} response is :{1}'.format(str(url), str(api_response.content)))
    except Exception as Err:
        raise ConnectorError(Err)

def _get_call(config,params):
    '''
    Process GET API Calls typically used for operational mode commands (fetch data)
    :param config: Connector's config params
    :param params: Action params
    :return: HTTP GET response
    '''
    method = '/' + params.get('command')
    method_params = params.get('method_params')
    return _api_request('get', method, config, params=method_params)

def _post_call(config,params):
    '''
    Process POST API Calls typically used in configuration mode (update config) it can also be used to fetch data within config mode
    :param config: Connector's config params
    :param params: Action params
    :return: HTTP Post response
    '''

    return _api_request('post', None, config, payload=payload)

def _check_health(config):
    try:
        if _api_request('get', '/get-software-information', config):
            return True
    except Exception as Err:
        logger.exception(str(Err))
        raise ConnectorError(str(Err))


operations = {
    'op_action': _get_call,
    'config_action': _post_call
}

