import logging

from flask import Flask, request, jsonify, Blueprint

from application.port.input import ProcessDistributorEventUseCase

logger = logging.getLogger(__name__)


class WebhookListener:
    def __init__(self, process_distributor_event_use_case: ProcessDistributorEventUseCase):
        self.process_distributor_event_use_case: ProcessDistributorEventUseCase = process_distributor_event_use_case

        self._listener = Blueprint("distributor_webhook_listener", __name__)

        self._init_handlers()

    def _init_handlers(self):
        @self._listener.route('/', methods=['POST'])
        def handler():
            event = request.json

            self.process_distributor_event_use_case.process(event)

            return jsonify(), 200

    def get_blueprint(self):
        return self._listener
