""" Copyright start
Copyright (C) 2008 - 2022 Fortinet Inc.
All rights reserved.
FORTINET CONFIDENTIAL & FORTINET PROPRIETARY SOURCE CODE
Copyright end """

from connectors.core.connector import Connector, get_logger, ConnectorError
from .operations import _check_health, operations
logger = get_logger('juniper_junos')

class Juniper_JunOS(Connector):
    def execute(self, config, operation, params, **kwargs):
        logger.info('In execute() Operation:[{}]'.format(operation))
        params.update({'operation':operation})
        operation = operations.get(operation, None)
        if not operation:
            logger.info('Unsupported operation [{}]'.format(operation))
            raise ConnectorError('Unsupported operation')
        return operation(config, params)

    def check_health(self, config):
        return _check_health(config)
