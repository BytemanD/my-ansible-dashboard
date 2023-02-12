

from easy2use.common import exceptions as exs


class EndpointNotFound(exs.BaseException):
    _msg = 'Endpoints for service:{service} region:{region} is not found'


class PipInstallFailed(exs.BaseException):
    _msg = 'Install {package} failed, cmd={}'
