from django.db import models


class Room(models.Model):
    key = models.CharField(max_length=5, unique=True)
    player1 = models.CharField(max_length=100)
    player2 = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.key
