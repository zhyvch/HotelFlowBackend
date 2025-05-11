from django.db import models
from django.utils.translation import gettext_lazy as _


class TimestampedBaseModel(models.Model):
    created_at = models.DateTimeField(verbose_name=_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated at'), auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class TitledBaseModel(models.Model):
    title = models.CharField(verbose_name=_('Title'), max_length=254)

    class Meta:
        abstract = True


class TitledTimestampedBaseModel(TitledBaseModel, TimestampedBaseModel):
    class Meta:
        abstract = True
