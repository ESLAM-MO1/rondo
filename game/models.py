from django.db import models


class Room(models.Model):
    key = models.CharField(max_length=10, unique=True)
    player1 = models.CharField(max_length=100)
    player2 = models.CharField(max_length=100, blank=True, null=True)

    # Ready system
    player1_ready = models.BooleanField(default=False)
    player2_ready = models.BooleanField(default=False)

    def __str__(self):
        return self.key


class GameImage(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    image_url = models.URLField()

    def __str__(self):
        return f"{self.name} - {self.category}"
