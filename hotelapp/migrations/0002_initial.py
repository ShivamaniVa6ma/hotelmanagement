# Generated by Django 5.1.5 on 2025-05-05 05:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('hotelapp', '0001_initial'),
        ('subscription', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='subscription',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subscribers', to='subscription.subscriptionplan'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
        migrations.AddField(
            model_name='aboutus',
            name='subscription_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='subscription.subscriptionuserdetails'),
        ),
        migrations.AddField(
            model_name='booking',
            name='subscription_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='subscription.subscriptionuserdetails'),
        ),
        migrations.AddField(
            model_name='contactmessage',
            name='subscription_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='subscription.subscriptionuserdetails'),
        ),
        migrations.AddField(
            model_name='event',
            name='subscription_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='subscription.subscriptionuserdetails'),
        ),
        migrations.AddField(
            model_name='facility',
            name='subscription_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='subscription.subscriptionuserdetails'),
        ),
        migrations.AddField(
            model_name='faq',
            name='subscription_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='subscription.subscriptionuserdetails'),
        ),
        migrations.AddField(
            model_name='feature',
            name='subscription_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subscription.subscriptionuserdetails'),
        ),
        migrations.AddField(
            model_name='fooditem',
            name='subscription_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='food_items', to='subscription.subscriptionuserdetails'),
        ),
        migrations.AddField(
            model_name='guest',
            name='subscription_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='guests', to='subscription.subscriptionuserdetails'),
        ),
        migrations.AddField(
            model_name='guest',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='guest_profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='booking',
            name='guest',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hotelapp.guest'),
        ),
        migrations.AddField(
            model_name='logosettings',
            name='subscription_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='subscription.subscriptionuserdetails'),
        ),
        migrations.AddField(
            model_name='profile',
            name='subscription_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profiles', to='subscription.subscriptionuserdetails'),
        ),
        migrations.AddField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='room',
            name='features',
            field=models.ManyToManyField(blank=True, to='hotelapp.feature'),
        ),
        migrations.AddField(
            model_name='room',
            name='subscription_plan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rooms', to='subscription.subscriptionplan'),
        ),
        migrations.AddField(
            model_name='room',
            name='subscription_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rooms', to='subscription.subscriptionuserdetails'),
        ),
        migrations.AddField(
            model_name='booking',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='hotelapp.room'),
        ),
        migrations.AddField(
            model_name='roomimage',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='hotelapp.room'),
        ),
        migrations.AddField(
            model_name='roomimage',
            name='subscription_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='room_images', to='subscription.subscriptionuserdetails'),
        ),
        migrations.AddField(
            model_name='roomtype',
            name='subscription_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='subscription.subscriptionuserdetails'),
        ),
        migrations.AddField(
            model_name='room',
            name='room_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rooms', to='hotelapp.roomtype'),
        ),
        migrations.AddField(
            model_name='service',
            name='subscription_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='subscription.subscriptionuserdetails'),
        ),
        migrations.AddField(
            model_name='spa',
            name='subscription_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='subscription.subscriptionuserdetails'),
        ),
        migrations.AddField(
            model_name='teamdesignation',
            name='subscription_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='subscription.subscriptionuserdetails'),
        ),
        migrations.AddField(
            model_name='teammember',
            name='designation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='hotelapp.teamdesignation'),
        ),
        migrations.AddField(
            model_name='teammember',
            name='subscription_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='team_members', to='subscription.subscriptionuserdetails'),
        ),
        migrations.AlterUniqueTogether(
            name='room',
            unique_together={('room_number', 'block', 'subscription_user')},
        ),
        migrations.AlterUniqueTogether(
            name='teammember',
            unique_together={('subscription_user', 'aadhar_no'), ('subscription_user', 'account_name'), ('subscription_user', 'account_number'), ('subscription_user', 'email1'), ('subscription_user', 'pan_no'), ('subscription_user', 'phone1')},
        ),
    ]
