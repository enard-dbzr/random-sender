import logging
import os

from flask import Flask

from application.service.process_distributor_event_service import ProcessDistributorEventService
from infrastructure.persistence.db_session import DBWorker
from infrastructure.webhook_listener import WebhookListener

DBWorker.init_db_file(os.getenv('DB_URL'))

app = Flask(__name__)

event_processor = ProcessDistributorEventService(os.getenv("DISTRIBUTOR_URL"), os.getenv("DISTRIBUTOR_TOKEN"))

webhook_listener = WebhookListener(event_processor)

app.register_blueprint(webhook_listener.get_blueprint())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001)
