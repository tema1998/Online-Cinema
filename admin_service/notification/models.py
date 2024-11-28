import uuid
import requests
from typing import Annotated

from users.models import User
from django.db import models


class TimeStampedMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

class PersonalNotification(TimeStampedMixin, UUIDMixin):
    topic = models.CharField(max_length=255)
    message = models.TextField()
    users = models.ManyToManyField(User)

    class Meta:
        verbose_name = 'Personal Notification'
        verbose_name_plural = 'Personal Notifications'

    def send(self) -> Annotated[int, "Status code"]:
        emails = [user.email for user in list(self.users.all())]

        # url = settings.EVENT_URL
        # url = '127.0.0.1'
        # payload = {
        #     "emails": emails,
        #     "topic": self.topic,
        #     "message": self.message,
        # }
        #
        # response = requests.post(url, json=payload)
        # return response.status_code
        print(emails)
        return None
