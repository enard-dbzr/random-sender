import requests
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from application.port.input.ProcessDistributorEventUseCase import ProcessDistributorEventUseCase
from infrastructure.persistence.db_session import DBWorker
from infrastructure.persistence.entity.feedback import Feedback
from infrastructure.persistence.entity.message import Message
from infrastructure.persistence.entity.sending import Sending


class ProcessDistributorEventService(ProcessDistributorEventUseCase):
    def __init__(self, distributor_url, auth_token):
        self.distributor_url = distributor_url
        self.auth_token = auth_token

    def _send_to_distributor(self, data: dict):
        response = requests.post(f"{self.distributor_url}/messages",
                                 json=data,
                                 headers={"Authorization": f"Bearer {self.auth_token}"})
        if response.status_code not in [200, 201]:
            raise Exception("Failed to send message", response.status_code, response.content)

        return response.json()

    def _clear_buttons(self, chat_id: int, message_id: int):
        requests.post(f"{self.distributor_url}/actions",
                      json={
                          "chatId": chat_id,
                          "payload": {
                              "type": "clear_buttons",
                              "messageId": message_id
                          }
                      })

    def process(self, event: dict):
        event_type = event['eventType']
        data = event['data']

        with DBWorker() as db:
            if event_type == "SESSION":
                if data["sessionEventType"] in ["CREATED", "STARTED"]:
                    chat_id = int(data["session"]["chatId"])
                    self._send_message(db, chat_id)
            elif event_type == "FEEDBACK":
                reply_to = int(data["replyTo"])
                self._process_feedback(db, reply_to, data["feedback"])
                self._send_message(db, int(data["feedback"]["chatId"]))

    def _send_message(self, db: Session, chat_id: int):
        unanswered = db.scalars(
            select(Sending)
            .where(Sending.chat_id == chat_id, Sending.is_processed == False,
                   Sending.reminder_to_id == None)
        ).first()

        if unanswered is not None:
            result = self._send_to_distributor({
                "chatId": chat_id,
                "content": {
                    "type": "reply",
                    "replyTo": unanswered.distributor_id,
                    "original": {
                        "type": "simple",
                        "text": "Ты не ответил на сообщение :(",
                        "attachments": []
                    }
                }
            })

            sending = Sending(
                distributor_id=result["messageId"],
                chat_id=chat_id,
                message=unanswered.message,
                is_processed=False,
                reminder_to=unanswered
            )

            db.add(sending)
            db.commit()

            return

        random_message: Message = db.scalars(select(Message).order_by(func.random())).first()

        result = self._send_to_distributor({
            "chatId": chat_id,
            "content": {
                "type": "simple",
                "text": random_message.text,
                "attachments": [
                    {"type": "button", "text": button, "tag": button} for button in random_message.buttons
                ],
            }
        })

        if result is not None:
            sending = Sending(
                distributor_id=result["messageId"],
                chat_id=chat_id,
                message=random_message,
                is_processed=False,
                reminder_to=None
            )

            db.add(sending)
            db.commit()

    def _process_feedback(self, db: Session, reply_to: int, feedback: dict):
        sending: Sending = db.scalars(select(Sending).where(Sending.distributor_id == reply_to)).first()

        clear = False

        if feedback["payload"]["type"] == "button":
            self._clear_buttons(int(feedback["chatId"]), feedback["payload"]["replyTo"])
            clear = True

        if sending is None:
            self._send_to_distributor({
                "chatId": int(feedback["chatId"]),
                "content": {
                    "type": "simple",
                    "text": "Сообщение, на которое вы отвечаете, не было найдено :( Попробуйте еще раз",
                    "attachments": [],
                }
            })
            return

        while sending.reminder_to is not None:
            sending = sending.reminder_to

        if sending.message.buttons and not clear:
            self._clear_buttons(sending.chat_id, sending.distributor_id)

        sending.is_processed = True

        feedback = Feedback(distributor_id=int(feedback["id"]), sending_id=sending.distributor_id)

        db.add(feedback)

        db.commit()
