from main.webinar import Webinar
from discord_webhook import DiscordWebhook, DiscordEmbed
from main.models import DiscordHistory, WebinarSession
from datetime import datetime


class DiscordClient:
    def __init__(self, webinar_session: WebinarSession, event_id: int) -> None:
        self.webinar_session = webinar_session
        self.event_id = event_id
        self.event = webinar_session.get_event(event_id)
        self.last_message = None

    def get_history_instance(self) -> None:
        discord_history = DiscordHistory.objects.filter(event_id=self.event_id)
        if discord_history.exists():
            self.history = discord_history.first()
        else:
            self.history = DiscordHistory(event_id=self.event_id)
            self.history.save()

    def send_message(self, message: Webinar.Message) -> None:
        time = datetime.strptime(message.createAt, '%Y-%m-%dT%H:%M:%S%z').time().strftime('%H:%M')
        webhook = DiscordWebhook(url=self.history.webhooks)
        embed = DiscordEmbed(description=message.text)
        embed.set_author(name=message.authorName)
        embed.set_footer(text=time)
        webhook.add_embed(embed)
        webhook.execute()

    def process(self) -> None:
        chat = self.webinar_session.get_chat(self.event.session_id)
        if len(chat.moderated) == 0:
            return
        for message in chat.moderated[-5:]:
            if message.id in self.history.message_ids:
                continue
            if self.history.active:
                self.send_message(message)
            self.history.message_ids.append(message.id)
            self.history.save()
