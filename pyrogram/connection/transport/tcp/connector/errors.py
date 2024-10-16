class ConnectorError(Exception):
    pass


class ConnectorProxyError(ConnectorError):
    pass


class ConnectorTimeoutError(ConnectorError, TimeoutError):
    pass


class ConnectorProxyTimeoutError(ConnectorProxyError, TimeoutError):
    pass
