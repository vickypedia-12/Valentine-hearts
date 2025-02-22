# Generated by Django 5.1.6 on 2025-02-08 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hearts', '0002_rename_personlity_traits_profile_personality_traits'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='zodiac_sign',
            field=models.CharField(blank=True, choices=[('ARI', 'Aries'), ('TAU', 'Taurus'), ('GEM', 'Gemini'), ('CAN', 'Cancer'), ('LEO', 'Leo'), ('VIR', 'Virgo'), ('LIB', 'Libra'), ('SCO', 'Scorpio'), ('SAG', 'Sagittarius'), ('CAP', 'Capricorn'), ('AQU', 'Aquarius'), ('PIS', 'Pisces')], max_length=3),
        ),
    ]
