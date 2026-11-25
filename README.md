# AgriSetu — Crop Disease Detection & Farmer–Guide Research Prototype

This V3 project is a fuller implementation of the Farmer/Guide block diagram supplied for the college research project.

## What is now working

### Farmer
- Role-based registration/login
- Farmer account and banking screens
- Crop disease detection form with banana image upload and trained Keras model support
- Soil screening using location, soil colour, river proximity and two images
- Crop selection decision support using local crops, weather and duration
- Beginner roadmap using crop, soil, weather, budget and precautions
- Less-labour service with crop/work-specific farm-machine video search
- Best-price module with crop + location + fertilization date, market comparison table, selling plan and official e-NAM links
- Local guide directory with Maharashtra locations, education, qualification and shop information
- ₹10 DEMO connection flow that reveals the guide contact in the presentation; it does not charge real money
- Feedback

### Guide
- Role-based registration/login
- Nearby farmer search
- Knowledge publishing and points
- Connected-farmer history after paid/demo connections
- Account/banking/feedback screens

## Data sources and honesty rules
The project includes reference/demo market values so the UI has meaningful data during a college presentation. They are explicitly labelled as reference/demo values and MUST NOT be presented as live prices.

For current market information, the UI links to official e-NAM live and historical price pages. e-NAM describes its platform as a pan-India electronic trading portal connecting APMC markets and provides price/trade information. Always verify current rates before real-world selling decisions.

The banana guidance in the project is intended as decision support. Image classification should not be treated as a definitive agronomic diagnosis; the app tells the farmer to verify with a qualified agricultural source.

## Run

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo_guides
python manage.py runserver
```

### Frontend
Open another terminal:
```bash
cd frontend
npm install
npm start
```
Open http://localhost:3000

## Demo guide accounts
After `python manage.py seed_demo_guides`:
- username: guide_pune_1 / password: demo1234
- username: guide_nashik_1 / password: demo1234
- username: guide_jalgaon_1 / password: demo1234

The other seeded demo guides are listed by the command output.

## Banana ML dataset
Put labelled folders under:
```text
ml/data/banana/
  Healthy/
  DiseaseClass1/
  DiseaseClass2/
```
Then run:
```bash
python ml/train.py --data_dir ml/data/banana --epochs 8
```
The trained files are written to `backend/ml_models/`.

## Real payment integration
The ₹10 flow is intentionally a demo for the college presentation. A production app should use a real payment provider with server-side order creation and payment verification. Never store card/UPI credentials in the database.

## Official references used for the market section
- e-NAM home: https://enam.gov.in/
- e-NAM live price: https://www.enam.gov.in/web/dashboard/live_price
- e-NAM historical trade data: https://www.enam.gov.in/web/dashboard/Historical
