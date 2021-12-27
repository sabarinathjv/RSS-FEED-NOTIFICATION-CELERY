from django.db import models
from django.contrib.auth.models import User

class Link(models.Model):

    title = models.CharField(max_length=250)
    link = models.TextField()
    subscribe = models.ManyToManyField(User,related_name="links",null=True,blank=True)
