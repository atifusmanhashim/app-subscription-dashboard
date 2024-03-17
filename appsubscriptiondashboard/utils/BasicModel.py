from django.db import models
from django.utils import timezone
from .constants import datetime_format

class BasicModel(models.Model):
    is_active = models.BooleanField(null=True, default=True, blank=True) 
    create_date = models.DateTimeField(default=timezone.now, blank=True)
    modified_date = models.DateTimeField(default=timezone.now, blank=True) 

    class Meta:
        abstract = True
    
    def formatted_create_date(self):
        return self.create_date.strftime(datetime_format)
    
    def formatted_modified_date(self):
        return self.modified_date.strftime(datetime_format)