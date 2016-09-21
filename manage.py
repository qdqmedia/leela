#!/usr/bin/env python
import os
import sys
import logging

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "leela.settings")

    from django.core.management import execute_from_command_line
    from raven import setup_logging
    from raven.contrib.django.handlers import SentryHandler

    setup_logging(SentryHandler(level=logging.WARNING))

    execute_from_command_line(sys.argv)
