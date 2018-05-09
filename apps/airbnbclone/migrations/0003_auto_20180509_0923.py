# Generated by Django 2.0.4 on 2018-05-09 09:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airbnbclone', '0002_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='average_rating',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='listing',
            name='number_reviews',
            field=models.IntegerField(default=0),
        ),
    ]
