"""
Models for news
"""

from django.db import models
from django.contrib.auth.models import User
from model_utils.models import TimeStampedModel

class NewsPage(TimeStampedModel):
    class Meta(object):
        app_label = "news"

    title = models.CharField(max_length=255, default="Empty")
    jacket = models.FileField(upload_to='jacket', null=True)
    summary = models.TextField(blank=True)
    content = models.TextField(blank=True)
    visible = models.BooleanField(default=True)
    author = models.ForeignKey(User, db_index=True)
    order_num = models.IntegerField()

    def access_check(self, user):
        return self.author == user

    def __repr__(self):
        return 'NewsPage<%r>' % ({
            'id': self.id,
            'title': self.title,
            'visible': self.visible,
            'author': self.author
        },)

    def __unicode__(self):
        return unicode(repr(self))
