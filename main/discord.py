from discord import Webhook, RequestsWebhookAdapter
from main.models import WebinarSession
from datetime import datetime


class DiscordClient:
    WEBHOOK_URL = 'https://discord.com/api/webhooks/847424948532281384/ca5xmuYDIBxmjxiq1u-_g6MXRgXpaYVsEj1lG3BT0IY-VHAEeA83zT74qv6OMAulc9cY'

    def __init__(self, webinar_session: WebinarSession, event_id: int) -> None:
        self.webinar_session = webinar_session
        self.event = webinar_session.get_event(event_id)
        self.last_message = None

    def print_last_message(self) -> None:
        chat = self.webinar_session.get_chat(self.event.session_id)
        if len(chat.moderated) > 0:
            message = chat.moderated[-1]
            if not hasattr(self.last_message, 'id') or message.id != self.last_message.id:
                self.last_message = message
                time = datetime.strptime(message.createAt, '%Y-%m-%dT%H:%M:%S%z').time().strftime('%H:%M')
                payload = f'`[{time}] {message.authorName}`\n{message.text}'
                Webhook.from_url(self.WEBHOOK_URL, adapter=RequestsWebhookAdapter()).send(payload)
