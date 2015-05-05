# -*- coding: utf-8 -*-
#
# This file is part of Flask-IIIF
# Copyright (C) 2015 CERN.
#
# Flask-IIIF is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Test signals and decorators."""

from unittest import TestCase

from flask import Flask, abort


class TestSignalsAndDecorators(TestCase):

    """Test signals and decorators."""

    def setUp(self):
        """Run before the test."""
        # Create an image in memory
        from flask_iiif import IIIF
        from flask_restful import Api

        app = Flask(__name__)
        app.config['DEBUG'] = True
        app.config['TESTING'] = True
        app.config['SERVER_NAME'] = "shield.worker.node.1"
        app.logger.disabled = True

        api = Api(app=app)

        iiif = IIIF(app=app)
        iiif.init_restful(api)

        self.app = app

    def tearDown(self):
        """Run after the test."""
        self.app = None

    def test_signals(self):
        """Test the signals."""
        from flask_iiif.signals import (
            iiif_after_process_request, iiif_after_validation,
            iiif_before_process_request
        )

        with self.app.app_context():
            @iiif_before_process_request.connect_via(self.app)
            def on_before_process(uuid):
                self.assertEqual(
                    uuid,
                    'ironman-mark-48'
                )

            @iiif_after_process_request.connect_via(self.app)
            def on_after_process(uuid):
                self.assertEqual(
                    uuid,
                    'ironman-mark-43'
                )

            @iiif_after_validation.connect_via(self.app)
            def on_after_validation(uuid):
                self.assertEqual(
                    uuid,
                    'j.a.r.v.i.s.'
                )

            # fire the signals
            iiif_before_process_request.send('ironman-mark-48')
            iiif_after_process_request.send('ironman-mark-43')
            iiif_after_validation.send('j.a.r.v.i.s.')

    def test_decorators(self):
        """Test decorators."""
        from flask_iiif.decorators import api_decorator
        from werkzeug.exceptions import Forbidden, InternalServerError

        with self.app.app_context():
            _iiif = self.app.extensions['iiif']

            def jarvis():
                return "Fight Ultron"

            _iiif.api_decorator_handler(jarvis)

            self.assertEqual(
                _iiif.api_decorator_callback(),
                "Fight Ultron"
            )

            @api_decorator
            def hulk():
                return "We are safe"

            self.assertEqual(
                hulk(),
                "We are safe"
            )

            def veronika():
                abort(403)

            _iiif.api_decorator_handler(veronika)

            @api_decorator
            def stark():
                return "We are safe"

            self.assertRaises(
                Forbidden,
                stark
            )

            def hydra():
                abort(500)

            _iiif.api_decorator_handler(hydra)

            self.assertRaises(
                InternalServerError,
                hydra
            )
