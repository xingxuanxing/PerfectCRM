# Generated by Django 4.0.5 on 2022-12-21 09:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0019_alter_userprofile_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userprofile',
            options={'permissions': (('crm_app_index', '可以允许所有app里的表'), ('crm_table_list', '可以查看每张表里的数据'), ('crm_table_change_view', '可以查看数据的修改页'), ('crm_table_list_change', '可以对数据进行修改'), ('crm_table_obj_add_view', '可以查看添加页'), ('crm_table_obj_add', '可以对数据进行添加'))},
        ),
    ]
