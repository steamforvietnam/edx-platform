from django.contrib.auth import get_user_model
from django.db import models
from model_utils.models import TimeStampedModel
from simple_history.models import HistoricalRecords

User = get_user_model()


class UserDemographics(TimeStampedModel):
    """
    A Users Demographics platform related data in support of the Demographics
    IDA and features
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    call_to_action_dismissed = models.BooleanField(default=False)
    history = HistoricalRecords()
