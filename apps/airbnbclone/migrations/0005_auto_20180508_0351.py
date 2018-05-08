# Generated by Django 2.0.4 on 2018-05-08 03:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airbnbclone', '0004_auto_20180507_1427'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='is_cancelled',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='availability',
            name='available',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='availability',
            name='one_day',
            field=models.DateField(unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='availability',
            unique_together={('listing', 'one_day')},
        ),
    ]