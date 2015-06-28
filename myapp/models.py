from django.db import models

# Create your models here.
class TweetUser(models.Model):
    tscreen_name = models.CharField(max_length=10, db_index=True, blank=True, null=True, default=None)
    tscreen_name = models.CharField(max_length=10, db_index=True, blank=True, null=True, default=None)
