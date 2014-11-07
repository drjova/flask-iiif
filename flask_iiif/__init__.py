# -*- coding: utf-8 -*-
#
# This file is part of Flask-IIIF
# Copyright (C) 2014 CERN.
#
# Flask-IIIF is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Multimedia and IIIF Image APIs.

Flask-IIIF is initialized like this:

Initialization of the extension:

>>> from flask import Flask
>>> from flask_iiif import IIIF
>>> app = Flask('myapp')
>>> ext = IIIF(app=app)

or alternatively using the factory pattern:

>>> app = Flask('myapp')
>>> ext = IIIF()
>>> ext.init_app(app)
"""

from __future__ import absolute_import


from flask import current_app, request
from six import string_types
from werkzeug.utils import cached_property, import_string

from . import config
from .version import __version__


class IIIF(object):

    """Flask extension implementation."""

    def __init__(self, app=None):
        """Initialize login callback."""
        self.uuid_to_path = None

        if app is not None:
            self.init_app(app)

    @cached_property
    def cache():
        """Return the cache handler."""
        handler = current_app.config['IIIF_CACHE_HANDLER']
        return import_string(handler) if isinstance(handler, string_types) \
            else handler

    def init_app(self, app):
        """Initialize a Flask application."""
        self.app = app
        # Follow the Flask guidelines on usage of app.extensions
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        if 'iiif' in app.extensions:
            raise RuntimeError("Flask application already initialized")
        app.extensions['iiif'] = self

        # Set default configuration
        for k in dir(config):
            if k.startswith('IIIF_'):
                self.app.config.setdefault(k, getattr(config, k))

    def init_restful(self, api):
        """Setup the urls."""
        from .restful import IIIFImageAPI

        api.add_resource(
            IIIFImageAPI,
            ("/api/multimedia/image/<string:version>/<string:uuid>/"
             "<string:region>/<string:size>/<string:rotation>/"
             "<string:quality>.<string:image_format>"),
        )

    def uuid_to_path_handler(self, callback):
        """Set the callback for the ``uuid`` to ``path`` convertion.

        :param callback: The callback for login.
        :type callback: function
        """
        self.uuid_to_path = callback


__all__ = ('IIIF', '__version__')
