from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial=True
    dependencies=[migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations=[
        migrations.CreateModel(name='Profile',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('role',models.CharField(choices=[('FARMER','Farmer'),('GUIDE','Guide')],max_length=10)),
            ('full_name',models.CharField(max_length=120)),('location',models.CharField(max_length=150)),
            ('contact_number',models.CharField(max_length=20)),('main_crop',models.CharField(blank=True,max_length=100)),
            ('education',models.CharField(blank=True,max_length=150)),('qualification',models.CharField(blank=True,max_length=200)),
            ('shop_name',models.CharField(blank=True,max_length=150)),('bank_name',models.CharField(blank=True,max_length=120)),
            ('account_number',models.CharField(blank=True,max_length=50)),('ifsc',models.CharField(blank=True,max_length=20)),
            ('points',models.PositiveIntegerField(default=0)),
            ('user',models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,related_name='profile',to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name='Disease',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('crop',models.CharField(max_length=80)),('germination_date',models.DateField()),('soil',models.CharField(max_length=80)),
            ('weather',models.CharField(max_length=80)),('image',models.ImageField(upload_to='disease/')),
            ('prediction',models.CharField(max_length=150)),('confidence',models.FloatField()),('advice',models.TextField()),
            ('created_at',models.DateTimeField(auto_now_add=True)),
            ('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name='SoilCheck',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('location',models.CharField(max_length=150)),('color',models.CharField(max_length=60)),('near_river',models.BooleanField()),
            ('soil_image',models.ImageField(blank=True,upload_to='soil/')),('farm_image',models.ImageField(blank=True,upload_to='farm/')),
            ('prediction',models.CharField(max_length=100)),('explanation',models.TextField()),('created_at',models.DateTimeField(auto_now_add=True)),
            ('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name='Connection',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('amount',models.DecimalField(decimal_places=2,default=10,max_digits=8)),('status',models.CharField(default='PENDING',max_length=20)),
            ('paid_at',models.DateTimeField(blank=True,null=True)),
            ('farmer',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='farmer_connections',to=settings.AUTH_USER_MODEL)),
            ('guide',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='guide_connections',to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name='Knowledge',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('crop',models.CharField(max_length=100)),('title',models.CharField(max_length=180)),('text',models.TextField()),
            ('points',models.PositiveIntegerField(default=10)),('created_at',models.DateTimeField(auto_now_add=True)),
            ('guide',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name='Feedback',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('rating',models.PositiveSmallIntegerField(default=5)),('message',models.TextField()),('created_at',models.DateTimeField(auto_now_add=True)),
            ('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to=settings.AUTH_USER_MODEL)),
        ]),
    ]
