from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

import uuid
import nanoid
import os
import string

# Create your models here.
class User(AbstractUser):
    def upload_dir(self, filename):
        extension = os.path.splitext(filename)[1].lower()
        file_suffix = nanoid.generate(string.ascii_letters + string.digits ,12)
        new_filename = f"{self.username}_{file_suffix}{extension}"

        return f"avatars/{new_filename}"

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=100, null=True)
    email = models.EmailField(unique=True)
    bio = models.TextField(null=True, blank=True)
    hackathon_participant = models.BooleanField(default=True)

    avatar = models.ImageField(default='user.png', upload_to=upload_dir)

    twitter = models.URLField(max_length=500, null=True, blank=True)
    linkedin = models.URLField(max_length=500, null=True, blank=True)
    website = models.URLField(max_length=500, null=True, blank=True)
    facebook = models.URLField(max_length=500, null=True, blank=True)
    github = models.URLField(max_length=500, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

class Event(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True)
    participants = models.ManyToManyField(User, blank=True, related_name='events')
    start_date = models.DateTimeField(null=True)
    registration_deadline = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-end_date']

    @property
    def event_status(self):
        now = timezone.now()

        if now < self.start_date:
            return "Upcoming"
        elif now < self.end_date:
            return "Ongoing"
        else:
            return "Finished"

    @property
    def registration_open(self):
        return timezone.now() < self.registration_deadline

class Submission(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    participant = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='submissions')
    event = models.ForeignKey(Event, null=True, on_delete=models.SET_NULL)
    details = models.TextField(null=True)

    def __str__(self):
        return str(self.event) + ' --- ' + str(self.participant)
