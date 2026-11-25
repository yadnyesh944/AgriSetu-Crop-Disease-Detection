import json
from pathlib import Path
from django.conf import settings
from pathlib import Path
from urllib.parse import quote_plus
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser,FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *

CROPS=["Banana","Cotton","Soybean","Sugarcane","Wheat","Jowar","Bajra","Rice","Onion","Grapes","Orange","Turmeric","Groundnut","Pigeon Pea (Tur)","Chickpea","Tomato","Maize","Pomegranate"]
SOILS=["Black Soil","Red Soil","Laterite Soil","Alluvial Soil","Coastal/Marine Soil","Brown/Forest Soil"]
WEATHER=["Hot & Dry","Hot & Humid","Moderate","Cool","High Rainfall","Low Rainfall"]

# These are REFERENCE/DEMO values for the college prototype, not live mandi quotations.
# The UI links to official e-NAM live/historical pages for real prices.
MARKETS={
 "Banana":[
  {"market":"Jalgaon","district":"Jalgaon","min":1800,"modal":2500,"max":3200,"unit":"quintal","note":"Major banana-growing region; compare grade, quality and buyer demand."},
  {"market":"Bhusawal","district":"Jalgaon","min":1700,"modal":2400,"max":3100,"unit":"quintal","note":"Compare transport cost with Jalgaon markets."},
  {"market":"Pune","district":"Pune","min":1900,"modal":2550,"max":3300,"unit":"quintal","note":"Check quality/size requirements before transport."},
 ],
 "Onion":[
  {"market":"Lasalgaon","district":"Nashik","min":1800,"modal":2600,"max":3500,"unit":"quintal","note":"Compare arrivals and grade before dispatch."},
  {"market":"Pimpalgaon","district":"Nashik","min":1750,"modal":2500,"max":3400,"unit":"quintal","note":"Check current mandi arrivals before selling."},
  {"market":"Pune","district":"Pune","min":1900,"modal":2700,"max":3600,"unit":"quintal","note":"Transport and quality deductions can affect net realization."},
 ],
 "Soybean":[
  {"market":"Latur","district":"Latur","min":4000,"modal":4500,"max":5000,"unit":"quintal","note":"Compare moisture and quality deductions."},
  {"market":"Akola","district":"Akola","min":3950,"modal":4480,"max":5050,"unit":"quintal","note":"Check current arrivals and quality."},
  {"market":"Hingoli","district":"Hingoli","min":3900,"modal":4420,"max":4980,"unit":"quintal","note":"Compare net price after transport."},
 ],
 "Cotton":[
  {"market":"Akola","district":"Akola","min":6500,"modal":7200,"max":7900,"unit":"quintal","note":"Grade, staple and moisture can affect realized price."},
  {"market":"Amravati","district":"Amravati","min":6400,"modal":7150,"max":7850,"unit":"quintal","note":"Compare buyer requirements and transport."},
  {"market":"Jalgaon","district":"Jalgaon","min":6300,"modal":7050,"max":7750,"unit":"quintal","note":"Check quality parameters before sale."},
 ],
 "Wheat":[
  {"market":"Pune","district":"Pune","min":2300,"modal":2550,"max":2800,"unit":"quintal","note":"Compare mandi and direct-buyer offers."},
  {"market":"Nashik","district":"Nashik","min":2250,"modal":2500,"max":2780,"unit":"quintal","note":"Check grain quality and moisture."},
  {"market":"Ahmednagar","district":"Ahilyanagar","min":2200,"modal":2480,"max":2750,"unit":"quintal","note":"Compare net realization after transport."},
 ],
 "Pomegranate":[
  {"market":"Solapur","district":"Solapur","min":5000,"modal":8000,"max":12000,"unit":"quintal","note":"Fruit grade, size and export quality can create large price differences."},
  {"market":"Sangli","district":"Sangli","min":4800,"modal":7600,"max":11500,"unit":"quintal","note":"Sort and grade before comparing buyers."},
  {"market":"Pune","district":"Pune","min":5200,"modal":8200,"max":12500,"unit":"quintal","note":"Check buyer grade specifications."},
 ],
 "Grapes":[
  {"market":"Nashik","district":"Nashik","min":3500,"modal":6500,"max":10000,"unit":"quintal","note":"Variety, berry quality and destination market strongly affect price."},
  {"market":"Sangli","district":"Sangli","min":3300,"modal":6200,"max":9500,"unit":"quintal","note":"Compare quality and packing requirements."},
 ],
 "Sugarcane":[
  {"market":"Kolhapur","district":"Kolhapur","min":2800,"modal":3100,"max":3400,"unit":"tonne","note":"Factory recovery and local procurement terms matter."},
  {"market":"Pune","district":"Pune","min":2700,"modal":3050,"max":3350,"unit":"tonne","note":"Confirm current factory procurement terms."},
 ],
}

PRICE_TIMING={
 "Banana":"Do not use a fixed 'highest price' month. Compare current mandi arrivals, grade and buyer demand close to harvest.",
 "Onion":"Price can change quickly with arrivals and storage availability. Check Lasalgaon/Pimpalgaon and nearby markets before dispatch.",
 "Soybean":"Compare current mandi modal prices and moisture/quality deductions before selling.",
 "Cotton":"Compare grade/staple/quality requirements and current buyer bids rather than relying on one historical rate.",
 "Grapes":"Harvest timing, variety, quality and destination buyer can materially change realization.",
 "Pomegranate":"Grading and buyer segment can create large price differences; compare several current offers.",
}

GUIDE_DATA={
 "Pune":[("Asha Patil","Pune","Agri Advisory Centre","BSc Agriculture","Crop Advisory","9000001001"),("Rohan Shinde","Pune","Green Farm Guidance","Diploma Agriculture","Horticulture","9000001002")],
 "Nashik":[("Mahesh Pawar","Nashik","Nashik Crop Help","BSc Agriculture","Viticulture","9000001003"),("Sneha Jadhav","Nashik","Kisan Mitra Centre","MSc Agriculture","Plant Protection","9000001004")],
 "Jalgaon":[("Vijay Chaudhari","Jalgaon","Banana Advisory Point","BSc Agriculture","Banana Crop Advisory","9000001005"),("Neha More","Jalgaon","Kisan Seva Shop","Diploma Agriculture","Soil & Crop Advisory","9000001006")],
 "Chhatrapati Sambhajinagar":[("Pratik Deshmukh","Chhatrapati Sambhajinagar","Marathwada Agri Help","BSc Agriculture","Agronomy","9000001007")],
 "Ahilyanagar":[("Kiran Kale","Ahilyanagar","Farm Guidance Centre","MSc Agriculture","Soil Science","9000001008")],
 "Latur":[("Sanjay Kadam","Latur","Soybean Advisory Centre","BSc Agriculture","Agronomy","9000001009")],
 "Akola":[("Nilesh Wankhede","Akola","Vidarbha Crop Help","BSc Agriculture","Cotton & Soybean","9000001010")],
 "Amravati":[("Pooja Rathod","Amravati","Farmer Guidance Point","MSc Agriculture","Plant Protection","9000001011")],
 "Solapur":[("Ganesh Jagtap","Solapur","Pomegranate Advisory","BSc Agriculture","Horticulture","9000001012")],
}

def token(u):return str(RefreshToken.for_user(u).access_token)
def pdata(p):return {"id":p.id,"username":p.user.username,"role":p.role,"full_name":p.full_name,"location":p.location,"contact_number":p.contact_number,"main_crop":p.main_crop,"education":p.education,"qualification":p.qualification,"shop_name":p.shop_name,"bank_name":p.bank_name,"account_number":p.account_number,"ifsc":p.ifsc,"points":p.points}

class Register(APIView):
 permission_classes=[AllowAny]
 def post(self,r):
  d=r.data
  if User.objects.filter(username=d.get("username")).exists():return Response({"error":"Username already exists"},400)
  if d.get("role") not in ["FARMER","GUIDE"]:return Response({"error":"Select Farmer or Guide"},400)
  u=User.objects.create_user(d.get("username"),password=d.get("password"));Profile.objects.create(user=u,role=d.get("role"),full_name=d.get("full_name"),location=d.get("location"),contact_number=d.get("contact_number"),main_crop=d.get("main_crop",""),education=d.get("education",""),qualification=d.get("qualification",""),shop_name=d.get("shop_name",""),bank_name=d.get("bank_name",""),account_number=d.get("account_number",""),ifsc=d.get("ifsc",""));return Response({"token":token(u),"profile":pdata(u.profile)},201)
class Login(APIView):
 permission_classes=[AllowAny]
 def post(self,r):
  u=authenticate(username=r.data.get("username"),password=r.data.get("password"))
  if not u:return Response({"error":"Invalid username or password"},401)
  return Response({"token":token(u),"profile":pdata(u.profile)})
class Me(APIView):
 def get(self,r):return Response(pdata(r.user.profile))
 def patch(self,r):
  p=r.user.profile
  for k in ["full_name","location","contact_number","main_crop","education","qualification","shop_name"]:
   if k in r.data:setattr(p,k,r.data[k])
  p.save();return Response(pdata(p))
class Banking(APIView):
 def patch(self,r):
  p=r.user.profile
  for k in ["bank_name","account_number","ifsc"]:
   if k in r.data:setattr(p,k,r.data[k])
  p.save();return Response(pdata(p))
class FeedbackAPI(APIView):
 def post(self,r):Feedback.objects.create(user=r.user,rating=r.data.get("rating",5),message=r.data.get("message",""));return Response({"message":"Feedback submitted"},201)
class Options(APIView):
 def get(self,r):return Response({"crops":CROPS,"soils":SOILS,"weather":WEATHER,"maharashtra_districts":sorted(set([x for k in GUIDE_DATA for x in [k]]))})
def get_disease_advice(disease):
    disease = disease.strip().lower()

    advice = {
        "sigatoka": """
Recommended Management:

1. Remove severely infected and dried banana leaves.
2. Dispose of affected leaves according to local agricultural guidance.
3. Maintain proper drainage around banana plants.
4. Keep the field free from excessive weeds.
5. Avoid overcrowding and manage excess suckers.
6. Consult a local agricultural expert for confirmation
   and further treatment recommendations.

Important:
This is an AI-based preliminary diagnosis.
Confirm the disease before deciding on treatment.
""",

        "healthy": """
Your uploaded leaf is classified as Healthy.

1. Continue regular crop monitoring.
2. Maintain proper field sanitation.
3. Provide suitable irrigation and crop nutrition.
4. Check leaves regularly for new symptoms.
""",

        "cordana": """
Possible Cordana leaf disease detected.

1. Monitor affected leaves regularly.
2. Maintain proper field sanitation.
3. Remove severely affected leaves where appropriate.
4. Consult an agricultural expert for confirmation
   and suitable management recommendations.
""",

        "pestalotiopsis": """
Possible Pestalotiopsis disease detected.

1. Monitor affected plants and leaves.
2. Maintain proper field sanitation.
3. Remove severely affected plant material where appropriate.
4. Consult an agricultural expert for confirmation
   and suitable management recommendations.
"""
    }

    return advice.get(
        disease,
        "Consult a local agricultural expert for disease confirmation and management."
    )
def ml_predict(f, crop):
    BASE_DIR = Path(__file__).resolve().parent.parent

    model = BASE_DIR / "ml_models" / "banana_model.keras"
    cp = BASE_DIR / "ml_models" / "class_names.json"

    print("\n========== MODEL DEBUG ==========")
    print("BASE_DIR:", BASE_DIR)
    print("MODEL PATH:", model)
    print("MODEL EXISTS:", model.exists())
    print("CLASS FILE PATH:", cp)
    print("CLASS FILE EXISTS:", cp.exists())
    print("SELECTED CROP:", repr(crop))
    print("CROP MATCH:", str(crop).strip().lower() == "banana")
    print("================================\n")

    if model.exists() and cp.exists() and str(crop).strip().lower() == "banana":
        import tensorflow as tf
        import numpy as np
        from PIL import Image

        m = tf.keras.models.load_model(model)
        classes = json.loads(cp.read_text())

        im = Image.open(f).convert("RGB").resize((224, 224))
        x = np.asarray(im, dtype="float32")

        pr = m.predict(x[None], verbose=0)[0]

        print("CLASS ORDER:", classes)
        print("ALL SCORES:", {
            classes[i]: round(float(pr[i]) * 100, 2)
            for i in range(len(classes))
        })

        i = int(pr.argmax())
        lab = classes[i]
        conf = float(pr[i])

        adv = get_disease_advice(lab)

        return lab, conf, adv

    return (
        "Model not trained yet",
        0,
        "Image received. Train the banana model with your labelled dataset to enable ML prediction."
    )
class DiseaseAPI(APIView):
 parser_classes=[MultiPartParser,FormParser]
 def post(self,r):
  if r.user.profile.role!="FARMER":return Response({"error":"Farmer access only"},403)
  f=r.FILES.get("image")
  if not f:return Response({"error":"Upload a crop/leaf image"},400)
  lab, conf, adv = ml_predict(f, r.data.get("crop"))

  o = Disease.objects.create(
    user=r.user,
    crop=r.data.get("crop", "Banana"),
    germination_date=r.data.get("germination_date") or None,
    soil=r.data.get("soil") or r.data.get("soil_type") or "",
    weather=r.data.get("weather") or "",
    image=f,
    prediction=lab,
    confidence=conf,
    advice=adv,
  )

  return Response({
    "prediction": lab,
    "confidence": conf,
    "advice": adv,
    "id": o.id
  }, 201)
class SoilAPI(APIView):
 parser_classes=[MultiPartParser,FormParser]
 def post(self,r):
  c=r.data.get("color","").lower();river=r.data.get("near_river")=="yes"
  if river:lab,exp="Alluvial Soil","River proximity may be associated with alluvial deposits. Confirm with a soil test before making major input decisions."
  elif "black" in c or "dark" in c:lab,exp="Black Soil","Dark/black colour can be consistent with black soil. Confirm texture, depth and laboratory soil-test results."
  elif "red" in c:lab,exp="Red Soil","Reddish colour can be consistent with red soil. Confirm with field texture and laboratory testing."
  elif "brown" in c:lab,exp="Brown/Forest Soil","Brown colour can occur in forest/hill regions; confirm with a soil test."
  else:lab,exp="Needs Field Verification","Colour, location and images are screening signals; laboratory testing is recommended."
  o=SoilCheck.objects.create(user=r.user,location=r.data.get("location",""),color=r.data.get("color",""),near_river=river,soil_image=r.FILES.get("soil_image"),farm_image=r.FILES.get("farm_image"),prediction=lab,explanation=exp);return Response({"prediction":lab,"explanation":exp,"next_steps":["Get a laboratory soil test for pH, organic carbon and available N-P-K.","Use the result with local crop recommendations before deciding fertilizer doses."]},201)
class CropIdea(APIView):
 def post(self,r):
  local=[x.strip().lower() for x in r.data.get("local_crops",[])];w=r.data.get("weather","").lower();duration=int(r.data.get("duration",120) or 120)
  cand=[("Bajra",90), ("Jowar",110), ("Groundnut",120), ("Chickpea",110), ("Pigeon Pea (Tur)",160)] if "dry" in w or "hot" in w else [("Rice",120),("Turmeric",210),("Maize",110),("Tomato",110),("Chickpea",110)]
  choices=[{"crop":x,"approx_duration_days":d,"reason":f"Fits the selected weather profile and requested duration of about {duration} days."} for x,d in cand if x.lower() not in local and d<=duration+60][:5]
  return Response({"suggested_crops":choices,"message":"These are decision-support suggestions, not a guarantee of yield or profit."})
class Roadmap(APIView):
 def post(self,r):
  c,s,w,b,loc=r.data.get("crop"),r.data.get("soil"),r.data.get("weather"),r.data.get("budget"),r.data.get("location","")
  return Response({"crop":c,"location":loc,"roadmap":[f"1. Field preparation: assess drainage and prepare the field for {s}.",f"2. Planting: use healthy, locally suitable {c} planting material.",f"3. Weather plan: organize irrigation/drainage and field work around {w} conditions.",f"4. Budget: divide the ₹{b} budget into land preparation, planting material, nutrients, irrigation, labour and contingency.","5. Weekly monitoring: inspect leaves, stems, roots and soil moisture.","6. Disease/pest response: identify symptoms early and consult a qualified local advisor before treatment.","7. Harvest & market: check maturity, quality requirements and current buyer/mandi information before harvest sale."],"precautions":["Do not apply pesticides only from an image prediction; confirm the diagnosis with a qualified agricultural source.","Use protective equipment and follow the product label if any approved input is used.","Keep records of dates, inputs, labour and costs.","Maintain drainage after heavy rainfall."]})
class Labour(APIView):
 def post(self,r):
  work=r.data.get("work","");crop=r.data.get("crop","");q=f'{work} mechanized farming machine {crop} Maharashtra'.replace(" ","+");return Response({"youtube_search":"https://www.youtube.com/results?search_query="+q,"machine_categories":["Power weeder","Rotavator","Mini tiller","Sprayer","Chaff cutter","Drip/irrigation equipment"],"note":"Choose equipment based on farm size, crop spacing, soil and local availability."})
class Price(APIView):
 def post(self,r):
  crop=r.data.get("crop","Banana");loc=r.data.get("location","").strip();fert=r.data.get("fertilization_time","")
  rows=MARKETS.get(crop,[])
  if loc: rows=sorted(rows,key=lambda x:0 if loc.lower() in (x["market"]+" "+x["district"]).lower() else 1)
  avg=round(sum(x["modal"] for x in rows)/len(rows)) if rows else None
  return Response({"crop":crop,"location":loc,"fertilization_time":fert,"reference_markets":rows,"average_reference_modal":avg,"price_status":"REFERENCE / DEMO DATA — verify live rates before selling","timing":PRICE_TIMING.get(crop,"Compare current mandi arrivals, quality and buyer offers close to sale date."),"selling_plan":["1. Grade and sort the produce.","2. Check current mandi arrivals and modal/min/max prices.","3. Compare at least 2–3 buyers after including transport, loading and commission costs.","4. Check e-NAM where the commodity/market is supported.","5. Keep weighment and payment records."],"online_options":[{"name":"e-NAM","url":"https://enam.gov.in/","description":"National Agriculture Market; official price/trading information and online market services."},{"name":"e-NAM Live Price","url":"https://www.enam.gov.in/web/dashboard/live_price","description":"Official live-price interface with state/APMC/commodity filters."},{"name":"e-NAM Historical Data","url":"https://www.enam.gov.in/web/dashboard/Historical","description":"Official historical trade-price interface."}]})
class Guides(APIView):
 def get(self,r):
  loc=r.query_params.get("location","").strip();q=Profile.objects.filter(role="GUIDE");
  if loc:q=q.filter(location__icontains=loc)
  data=[{"id":p.id,"name":p.full_name,"location":p.location,"shop_name":p.shop_name,"education":p.education,"qualification":p.qualification,"points":p.points,"demo":False} for p in q]
  # Add fictional demo guides only when requested, so the screen never looks empty in a college presentation.
  if not data and loc:
   for i,(name,gloc,shop,edu,qual,phone) in enumerate(GUIDE_DATA.get(loc,[]),1):
    data.append({"id":-i,"name":name,"location":gloc,"shop_name":shop,"education":edu,"qualification":qual,"points":0,"demo":True,"contact_number":phone})
  return Response(data)
class GuidePayment(APIView):
 def post(self,r):
  p=Profile.objects.filter(id=r.data.get("guide_id"),role="GUIDE").first()
  demo=False
  if not p:
   # Demo directory records use negative IDs; never create a financial record for them.
   did=abs(int(r.data.get("guide_id",0)))
   for loc,items in GUIDE_DATA.items():
    if did and did<=len(items):
     name,gloc,shop,edu,qual,phone=items[did-1];demo=True;break
   if not demo:return Response({"error":"Guide not found"},404)
  if demo:
   return Response({"status":"DEMO_PAID","amount":10,"demo":True,"guide":{"name":name,"contact_number":phone,"location":gloc,"shop_name":shop},"payment_id":"DEMO-10","message":"Demo payment recorded for presentation. No real money was charged."},201)
  c=Connection.objects.create(farmer=r.user,guide=p.user,amount=10,status="PAID",paid_at=timezone.now());return Response({"status":"PAID","amount":10,"demo":False,"guide":{"name":p.full_name,"contact_number":p.contact_number,"location":p.location,"shop_name":p.shop_name},"payment_id":c.id},201)
class DiseaseHistory(APIView):
 def get(self,r):return Response(list(Disease.objects.filter(user=r.user).values("id","crop","prediction","confidence","advice","created_at")))
class GuideFarmers(APIView):
 def get(self,r):
  q=Profile.objects.filter(role="FARMER");loc=r.query_params.get("location","")
  if loc:q=q.filter(location__icontains=loc)
  return Response([{"name":p.full_name,"location":p.location,"main_crop":p.main_crop} for p in q])
class GuideKnowledge(APIView):
 def get(self,r):return Response(list(Knowledge.objects.order_by("-created_at").values("crop","title","text","points","created_at")))
 def post(self,r):
  o=Knowledge.objects.create(guide=r.user,crop=r.data.get("crop"),title=r.data.get("title"),text=r.data.get("text"),points=10);p=r.user.profile;p.points+=10;p.save();return Response({"points":10,"title":o.title},201)
class GuideHistory(APIView):
 def get(self,r):
  q=Connection.objects.filter(guide=r.user,status="PAID").select_related("farmer__profile");return Response([{"farmer_name":x.farmer.profile.full_name,"location":x.farmer.profile.location,"amount":float(x.amount),"paid_at":x.paid_at} for x in q])
