# Generated by Django 4.2.3 on 2023-07-29 17:59

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shared', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('basemodel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='shared.basemodel')),
                ('body', models.TextField(validators=[django.core.validators.MaxLengthValidator(500)])),
            ],
            bases=('shared.basemodel',),
        ),
        migrations.CreateModel(
            name='CommentLike',
            fields=[
                ('basemodel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='shared.basemodel')),
            ],
            bases=('shared.basemodel',),
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('basemodel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='shared.basemodel')),
                ('post_image', models.ImageField(blank=True, null=True, upload_to='posts/images/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpeg', 'jpg', 'jfif', 'heif', 'png', 'avif'])], verbose_name='Post Image')),
                ('caption', models.TextField(validators=[django.core.validators.MaxLengthValidator(1000)])),
            ],
            options={
                'verbose_name': 'post',
                'verbose_name_plural': 'posts',
                'db_table': 'posts',
            },
            bases=('shared.basemodel',),
        ),
        migrations.CreateModel(
            name='PostLike',
            fields=[
                ('basemodel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='shared.basemodel')),
            ],
            bases=('shared.basemodel',),
        ),
    ]
