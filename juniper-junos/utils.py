""" Copyright start
Copyright (C) 2008 - 2022 Fortinet Inc.
All rights reserved.
FORTINET CONFIDENTIAL & FORTINET PROPRIETARY SOURCE CODE
Copyright end """

#
# Utilities
#
import re
import validators
import xmltodict
from connectors.core.connector import get_logger, ConnectorError
from .constants import *

logger = get_logger('juniper_junos')

def input_validator(parameter,type_of_param):
    '''
    Validates user input
    :param parameter: value to validate
    :param type_of_param: IP, FQDN, Wildcard
    :return: True if valid False if not
    '''
    if type_of_param =='ip-prefix':
        if not validators.ipv4_cidr(parameter) and not validators.ipv4(parameter) and not validators.ipv6_cidr(parameter) and not validators.ipv6(parameter):
            return False
    elif type_of_param =='dns-name':
        if not validators.domain(parameter):
            return False
    elif type_of_param =='wildcard-address':
        address = parameter.split('/')[0]
        mask = parameter.split('/')[1]
        if not validators.ipv4(address) or not validators.ipv4(mask):
            return False
    return True

def parse_prefix_list_params(params):
    '''
    Parses user params and creates the POST payload for the API call. the defined param address_to_[add|delete]
    determines the action to take
    :param params.prefix_list: name of the prefix list in JunOS
    :param params.address_to_add: one or more (in CSV) list of addresses to add
    :param params.address_to_delete: one or more (in CSV) list of addresses to delete
    :return: POST XML payload
    '''
    IP_PREFIX = 'ip-prefix'
    address_list = []
    prefix_list = params.get('prefix_list')
    address_to_add = params.get('address_to_add')
    address_to_delete = params.get('address_to_delete')
    target_object = address_to_add if address_to_add else address_to_delete
    if ',' in target_object:
        target_object = target_object.replace(' ', '').split(',')
        for obj in target_object:
            if not input_validator(obj,IP_PREFIX):
                logger.error('Entered value: {0} is not a valid: {1}'.format(obj,IP_PREFIX))
                raise ConnectorError('Entered value: {0} is not a valid: {1}'.format(obj,IP_PREFIX))
            if address_to_add:
                address_list.append(ADDRESS_OBJECT['prefix-list-add-item'].format(obj))
            elif address_to_delete:
                address_list.append(ADDRESS_OBJECT['prefix-list-delete-item'].format(obj))
    else:
        if not input_validator(target_object, IP_PREFIX):
            logger.error('Entered value: {0} is not a valid: {1}'.format(target_object, IP_PREFIX))
            raise ConnectorError('Entered value: {0} is not a valid: {1}'.format(target_object, IP_PREFIX))
        if address_to_add:
            address_list.append(ADDRESS_OBJECT['prefix-list-add-item'].format(target_object))
        elif address_to_delete:
            address_list.append(ADDRESS_OBJECT['prefix-list-delete-item'].format(target_object))

    payload = PREFIX_LIST.format(NAME=prefix_list,
                                 PREFIX_LIST=' '.join(address_list))
    return payload

def parse_address_set_params(params):
    '''
    Parses user params and creates the POST payload for the API call. the defined param object_to_[add|delete]
    determines the action to take
    :param params.address_set: name of the address set in the in JunOS's global address book
    :param params.object_type: IP, FQDN, Wildcard as defined in constants.py/ADDRESS_OBJECT
    :param params.object_to_add: one or more (in CSV) list of objects to add
    :param params.object_to_delete: one or more (in CSV) list of objects to delete
    :return: POST XML Payload
    '''
    address_list = []
    address_name = []
    address_set = params.get('address_set')
    object_type = params.get('object_type')
    object_to_add = params.get('object_to_add')
    object_to_delete = params.get('object_to_delete')
    target_object = object_to_add if object_to_add else object_to_delete

    if ',' in target_object:
        target_object = target_object.replace(' ', '').split(',')
        for obj in target_object:
            if not input_validator(obj,object_type):
                logger.error('Entered value: {0} is not a valid: {1}'.format(obj,object_type))
                raise ConnectorError('Entered value: {0} is not a valid: {1}'.format(obj,object_type))
            if object_to_add:
                object_definition = ADDRESS_OBJECT[object_type].format(obj)
                address_list.append(ADDRESS_OBJECT['address-book-add-entry'].format(NAME=obj,ENTRY=object_definition))
                address_name.append(ADDRESS_OBJECT['address-set-add-entry'].format(NAME=obj))
            elif object_to_delete:
                address_list.append(ADDRESS_OBJECT['address-book-delete-entry'].format(NAME=obj))
                address_name.append(ADDRESS_OBJECT['address-set-delete-entry'].format(NAME=obj))
    else:
        if not input_validator(target_object, object_type):
            logger.error('Entered value: {0} is not a valid: {1}'.format(target_object, object_type))
            raise ConnectorError('Entered value: {0} is not a valid: {1}'.format(target_object, object_type))
        if object_to_add:
            object_definition = ADDRESS_OBJECT[object_type].format(target_object)
            address_list.append(ADDRESS_OBJECT['address-book-add-entry'].format(NAME=target_object, ENTRY=object_definition))
            address_name.append(ADDRESS_OBJECT['address-set-add-entry'].format(NAME=target_object))
        elif object_to_delete:
            address_list.append(ADDRESS_OBJECT['address-book-delete-entry'].format(NAME=target_object))
            address_name.append(ADDRESS_OBJECT['address-set-delete-entry'].format(NAME=target_object))

    payload = CONFIG_GLOBAL_ADDRESS_BOOK.format(ADDRESS_LIST=' '.join(address_list),
                                                ADDRESS_SET_NAME=address_set,
                                                ADDRESS_NAME_LIST=' '.join(address_name))
    return payload

def parse_config_xml_response(response):
    '''
    Parses JunOS configuration action response and extracts its XML, fixes it and converts it to JSON
    :param response: Raw server response
    :return: JSON formatted response
    '''
    xml_response = re.findall(r'\<.*\>', response)
    if len(xml_response) > 0:
        return_data = '<response>{0}</response>'.format(''.join(xml_response).replace('\\', ''))
        json_return_data = xmltodict.parse(return_data)
        if 'xnm:error' in return_data:
            logger.error('Request failed with Error: {0}'.format(json_return_data))
            raise ConnectorError('Request failed with Error: {0}'.format(json_return_data))
        return xmltodict.parse(return_data)

def parse_op_xml_response(response_data):
    '''
    Parses JunOS operational mode action response and extracts its XML, fixes it and converts it to JSON
    :param response: Raw server response
    :return: JSON formatted response
    '''
    xml_response = re.search(r'\<data.*data\>', response_data, re.DOTALL).group(0)
    if xml_response:
        return xmltodict.parse(xml_response)

def get_config(config):
    '''
    Returns JunOS config attributes
    '''
    device_url = config.get('device_url').strip('/').strip()
    tcp_port = config.get('tcp_port')
    username = config.get('username')
    password = config.get('password')
    verify_ssl = config.get('verify_ssl')
    if device_url[:7] != 'http://' and device_url[:8] != 'https://':
        device_url = 'https://{}'.format(device_url)
    return device_url, tcp_port, username, password, verify_ssl