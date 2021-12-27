# Generated by Django 3.2.10 on 2021-12-26 13:11

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250)),
                ('link', models.TextField()),
                ('subscribe', models.ManyToManyField(blank=True, null=True, related_name='subscribe', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]