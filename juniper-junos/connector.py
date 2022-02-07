from connectors.core.connector import Connector, get_logger, ConnectorError
from .operations import _check_health, operations
logger = get_logger('juniper_junos')

class Juniper_JunOS(Connector):
    def execute(self, config, operation, params, **kwargs):
        logger.info('In execute() Operation:[{}]'.format(operation))
        operation = operations.get(operation, None)
        if not operation:
            logger.info('Unsupported operation [{}]'.format(operation))
            raise ConnectorError('Unsupported operation')
        result = operation(config, params)
        return result

    def check_health(self, config):
        return _check_health(config)
