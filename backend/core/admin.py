from django.contrib import admin
from .models import Profile,Disease,SoilCheck,Connection,Knowledge,Feedback
admin.site.register([Profile,Disease,SoilCheck,Connection,Knowledge,Feedback])
