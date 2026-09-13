from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import SET_NULL
import uuid
import os

# Create your models here.
class User(AbstractUser):
    def upload_dir(self, filename):
        extension = os.path.splitext(filename)[1]
        new_filename = f"{uuid.uuid4()}{extension}"

        return f"users/{self.id}/{new_filename}"

    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=100, null=True)
    email = models.EmailField(unique=True)
    bio = models.TextField(null=True, blank=True)
    hackathon_participant = models.BooleanField(default=True)

    avatar = models.ImageField(default='users/avatar_pnrczr.png', upload_to=upload_dir)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

class Event(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
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

class Submission(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    participant = models.ForeignKey(User, null=True, on_delete=SET_NULL, related_name='submissions')
    event = models.ForeignKey(Event, null=True, on_delete=SET_NULL)
    details = models.TextField(null=True)

    def __str__(self):
        return str(self.event) + ' --- ' + str(self.participant)
