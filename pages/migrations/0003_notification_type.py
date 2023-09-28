# Generated by Django 4.2.5 on 2023-09-28 21:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='type',
            field=models.CharField(choices=[('test', 'test'), ('new_thread', 'new_thread'), ('new_repost', 'new_repost'), ('new_quote', 'new_quote'), ('new_subscriber', 'new_subscriber'), ('subscribe_request', 'subscribe_request'), ('unsubscribe_request', 'unsubscribe_request'), ('follow', 'follow'), ('unfollow', 'unfollow'), ('subscribe_allowed', 'subscribe_allowed'), ('unsubscribe_allowed', 'unsubscribe_allowed'), ('new_like', 'new_like'), ('new_dislike', 'new_dislike'), ('new_comment', 'new_comment'), ('new_mention', 'new_mention')], default='test', max_length=20),
            preserve_default=False,
        ),
    ]
