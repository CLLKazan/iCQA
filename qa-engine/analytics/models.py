from django.db import models
from forum.models import Question

class Satisfaction(models.Model):
    question = models.OneToOneField(Question)
    score = models.FloatField()
