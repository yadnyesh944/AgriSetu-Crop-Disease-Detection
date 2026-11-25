from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Profile

GUIDES=[
("guide_pune_1","Asha Patil","Pune","Agri Advisory Centre","BSc Agriculture","Crop Advisory","9000001001"),
("guide_pune_2","Rohan Shinde","Pune","Green Farm Guidance","Diploma Agriculture","Horticulture","9000001002"),
("guide_nashik_1","Mahesh Pawar","Nashik","Nashik Crop Help","BSc Agriculture","Viticulture","9000001003"),
("guide_nashik_2","Sneha Jadhav","Nashik","Kisan Mitra Centre","MSc Agriculture","Plant Protection","9000001004"),
("guide_jalgaon_1","Vijay Chaudhari","Jalgaon","Banana Advisory Point","BSc Agriculture","Banana Crop Advisory","9000001005"),
("guide_jalgaon_2","Neha More","Jalgaon","Kisan Seva Shop","Diploma Agriculture","Soil & Crop Advisory","9000001006"),
("guide_sambhajinagar","Pratik Deshmukh","Chhatrapati Sambhajinagar","Marathwada Agri Help","BSc Agriculture","Agronomy","9000001007"),
("guide_ahilyanagar","Kiran Kale","Ahilyanagar","Farm Guidance Centre","MSc Agriculture","Soil Science","9000001008"),
("guide_latur","Sanjay Kadam","Latur","Soybean Advisory Centre","BSc Agriculture","Agronomy","9000001009"),
("guide_akola","Nilesh Wankhede","Akola","Vidarbha Crop Help","BSc Agriculture","Cotton & Soybean","9000001010"),
("guide_amravati","Pooja Rathod","Amravati","Farmer Guidance Point","MSc Agriculture","Plant Protection","9000001011"),
("guide_solapur","Ganesh Jagtap","Solapur","Pomegranate Advisory","BSc Agriculture","Horticulture","9000001012"),
]
class Command(BaseCommand):
 def handle(self,*args,**kwargs):
  for username,name,loc,shop,edu,qual,phone in GUIDES:
   u,created=User.objects.get_or_create(username=username)
   if created:u.set_password("demo1234");u.save()
   Profile.objects.update_or_create(user=u,defaults={"role":"GUIDE","full_name":name,"location":loc,"contact_number":phone,"education":edu,"qualification":qual,"shop_name":shop})
  self.stdout.write(self.style.SUCCESS("12 demo guide profiles ready. Password for demo guides: demo1234"))
