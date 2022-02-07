import requests, logging
from requests.auth import HTTPBasicAuth
from connectors.core.connector import get_logger, ConnectorError
from requests_toolbelt.utils import dump

logger = get_logger('juniper_junos')
logger.setLevel(logging.DEBUG) #Disable for prod

# Globals/Endpoints
JUNOS_URL='{0}:{1}/rpc/{2}'
GET_SOFTWARE_INFO = 'get-software-information'



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


def _api_request(method, endpoint, config, payload={}, header=None, params={}, response_format='json'):
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



def _check_health(config):
    try:
        if _api_request('get', GET_SOFTWARE_INFO, config):
            return True
    except Exception as Err:
        logger.exception(str(Err))
        raise ConnectorError(str(Err))


operations = {
    'get-software-information': _api_request
}

