# Generated by Django 2.0.4 on 2018-05-11 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airbnbclone', '0009_merge_20180510_0957'),
    ]

    operations = [
        migrations.AlterField(
            model_name='amenity',
            name='font_class',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='amenity',
            name='name',
            field=models.CharField(max_length=50),
        ),
    ]
