""" Copyright start
Copyright (C) 2008 - 2022 Fortinet Inc.
All rights reserved.
FORTINET CONFIDENTIAL & FORTINET PROPRIETARY SOURCE CODE
Copyright end """

import requests, logging, json
from requests.auth import HTTPBasicAuth
from connectors.core.connector import get_logger, ConnectorError
from .utils import *
from .constants import *
from requests_toolbelt.utils import dump

logger = get_logger('juniper_junos')



def _check_health(config):
    try:
        if _api_request('get', '/get-software-information', config):
            return True
    except Exception as Err:
        logger.exception(str(Err))
        raise ConnectorError(str(Err))


def _api_request(method, endpoint, config, payload={}, header=HTTP_HEADERS, params={}):
    try:
        device_url, tcp_port, username, password, verify_ssl = get_config(config)
        url = JUNOS_URL.format(device_url,tcp_port,endpoint)
        if method in ['post']:
            params.update({'stop-on-error':'1'})
        api_response = requests.request(method=method, url=url, auth=HTTPBasicAuth(username, password), headers=header, params=params, data=payload, verify=verify_ssl)
        logger.debug('REQUESTS_DUMP:\n{}'.format(dump.dump_all(api_response).decode('utf-8')))                                        
        if api_response.ok:
            try:
                logger.debug('Device response is not a valid JSON falling back to str')
                return api_response.json()
            except:
                return api_response.content.decode('utf-8')
        else:
            logger.info('Fail To request API {0} response is : {1}'.format(str(url), str(api_response.content)))
            raise ConnectorError('Fail To request API {0} response is : {1}'.format(str(url), str(api_response.content)))
    except Exception as Err:
        logger.error('API Request Error: {0}'.format(str(Err)))
        raise ConnectorError(Err)


def _get_call(config,params):
    '''
    Process GET API Calls typically used for operational mode commands (fetch data)
    :param config: Connector's config params
    :param params: Action params
    :return: HTTP GET response
    '''
    method_params = params.get('method_params') if params.get('method_params') else None
    method = '/' + params.get('method') if params.get('method') else '/' + params.get('custom_method')
    if len(method) < 6:
        logger.error('Command cannot be empty, pick either a command or a custom command param')
        raise ConnectorError('Command cannot be empty, pick either a command or a custom command param')
    HTTP_HEADERS.update({'Accept':'application/json','Content-Type': 'application/xml'})
    return _api_request('get', method, config, params=method_params)


def _post_call(config,params):
    '''
    Process POST API Calls typically used in configuration mode (update config) it can also be used to fetch data within config mode
    :param config: Connector's config params
    :param params: Action params
    :return: HTTP Post response
    '''
    HTTP_HEADERS.update({'Accept':'application/xml','Content-Type': 'application/xml'})
    request_payload = params.get('request_payload',None)
   
    if not request_payload:
        logger.error('Payload cannot be empty')
        raise ConnectorError('Payload cannot be empty')
    response = _api_request('post', '', config, payload=request_payload)
    return parse_config_xml_response(response)


def get_address_set(config,params):
    '''
    Returns address set set content or items count
    :param config: Connector's config params
    :param params.address_set: name of the address set to return
    :param params.get_count: bool : is True returns nothing but items count
    :return: address set data or count
    '''
    address_set = params.get('address_set', None)
    get_count = params.get('get_count', None)
    payload = GET_CONFIG.format(GLOBAL_ADDRESS_SET.format(address_set))
    HTTP_HEADERS.update({'Content-Type': 'application/xml'})
    response = _api_request('post', '', config, payload=payload)
    try:
        if get_count is True:
            json_response = parse_op_xml_response(response)
            return {'item_count':len(json_response['data']['configuration']['security']['address-book']['address-set']['address'])}
        else:
            return parse_op_xml_response(response)
    except Exception as Err:
        logger.info('get_address_set Error: {0}'.format(str(Err)))
        raise ConnectorError(Err)


def _add_delete_address(config,params):
    '''
    Adds to or Deletes from an address set within the global address book
    :param config: Connector's config params
    :param params: action params as defined in info.json
    :return: JunOS action response
    '''
    HTTP_HEADERS.update({'Accept':'application/xml','Content-Type': 'application/xml'})
    payload = parse_address_set_params(params)
    payload = CONFIG_COMMIT.format(payload)
    logger.debug(payload)
    try:
        response = _api_request('post', '', config, payload=payload)
        logger.debug(response)
        return parse_config_xml_response(response)
    except Exception as Err:
        logger.error('_add_delete_address Error: {0}'.format(str(Err)))
        raise ConnectorError(Err)


def get_prefix_list(config,params):
    '''
    Returns prefix list content or items count
    :param config: Connector's config params
    :param params.prefix_list: name of the prefix list to return
    :param params.get_count: bool : is True returns nothing but items count
    :return: address set data or count
    '''
    prefix_list = params.get('prefix_list', None)
    get_count = params.get('get_count', None)
    payload = GET_CONFIG.format(PREFIX_LIST.format(NAME=prefix_list,PREFIX_LIST=''))
    HTTP_HEADERS.update({'Content-Type': 'application/xml'})
    response = _api_request('post', '', config, payload=payload)
    try:
        if get_count is True:
            json_response = parse_op_xml_response(response)
            return {'item_count':len(json_response['data']['configuration']['policy-options']['prefix-list']['prefix-list-item'])}
        else:
            return parse_op_xml_response(response)
    except Exception as Err:
        logger.info('get_prefix_list Error: {0}'.format(str(Err)))
        raise ConnectorError(Err)


def _add_delete_prefix_list(config,params):
    '''
    Adds to or Deletes items from a prefix list
    :param config: Connector's config params
    :param params: action params as defined in info.json
    :return: JunOS action response
    '''
    HTTP_HEADERS.update({'Accept':'application/xml','Content-Type': 'application/xml'})
    payload = parse_prefix_list_params(params)
    payload = CONFIG_COMMIT.format(payload)
    logger.debug(payload)
    try:
        response = _api_request('post', '', config, payload=payload)
        logger.debug(response)
        return parse_config_xml_response(response)
    except Exception as Err:
        logger.info('_add_delete_prefix_list Error: {0}'.format(str(Err)))
        raise ConnectorError(Err)


operations = {
    'op_action': _get_call,
    'config_action': _post_call,
    'get_address_set': get_address_set,
    'add_to_address_set': _add_delete_address,
    'delete_from_address_set': _add_delete_address,
    'get_prefix_list': get_prefix_list,
    'add_to_prefix_list': _add_delete_prefix_list,
    'delete_from_prefix_list': _add_delete_prefix_list
}

