# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

from .version import __version__, __version_info__
from .protocol import ASTMProtocol
from .client import Client
from astm.server import RequestHandler, Server

import logging
log = logging.getLogger()

class NullHandler(logging.Handler):
    def emit(self, *args, **kwargs):
        pass

log.addHandler(NullHandler())
