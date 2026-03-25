from django.db import models

from user_auth.models import User


class Item(models.Model):
    __tablename__ = "items"

    name = models.CharField(max_length=100, unique=True, blank=False, null=False)
    owner = models.ForeignKey(User, on_delete=models.PROTECT)
