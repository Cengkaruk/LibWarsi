#! /usr/bin/python
# based on python-irgsh exception 
#

class WarsiGeneralError(Exception):
    _msg = None

    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return self._msg

class WarsiExtractError(WarsiGeneralError):
    def __init__(self, msg):
        self._msg = msg

class WarsiInfoError(WarsiGeneralError):
    def __init__(self, msg):
        self._msg = msg

class WarsiManifestError(WarsiGeneralError):
    def __init__(self, msg):
        self._msg = msg

class WarsiCopyDebPackage(WarsiGeneralError):
    def __init__(self, msg):
        self._msg = msg

class WarsiIOError(WarsiGeneralError):
    def __init__(self, msg):
        self._msg = msg

class BuildGeneralError(Exception):
    _msg = None

    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return self._msg

class BuildDownloadError(BuildGeneralError):
    def __init__(self, msg):
        self._msg = msg

class BuildPreparationError(BuildGeneralError):
    def __init__(self, msg):
        self._msg = msg

class BuildBuilderGeneralError(BuildGeneralError):
    def __init__(self, msg):
        self._msg = msg

class BuildBuilderConfigurationError(BuildGeneralError): 
    def __init__(self, msg):
        self._msg = msg

class BuildBuilderFailureError(BuildGeneralError):
    def __init__(self, msg):
        self._msg = msg

