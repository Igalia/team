from django.db import models


class Person(models.Model):
    login = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.login
