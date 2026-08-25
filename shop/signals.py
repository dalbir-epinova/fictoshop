"""Signal handlers that ensure demo data exists."""

from __future__ import annotations

from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .bootstrap import bootstrap


@receiver(post_migrate)
def populate_defaults(sender, **kwargs):
    if sender.name != "shop":
        return
    bootstrap()
