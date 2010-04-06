from badgeGen import build_badge as buildFunc
from celery.decorators import task
from celery.task import Task
from django.core.cache import cache
from models import Game
from bk import BKTree

@task()
def build_badge(badge):
	return buildFunc(badge)

