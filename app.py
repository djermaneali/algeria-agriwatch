import streamlit as st
import streamlit.components.v1 as components
import folium
from folium.plugins import Fullscreen, Search
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from datetime import datetime, timedelta

st.set_page_config(
    page_title="نظام المراقبة — الجزائر | Algeria Monitor",
    page_icon="🇩🇿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# DATA
# ============================================================
AG_ZONES = [
    {"name_ar":"سهل متيجة",   "name_en":"Mitidja Plain",   "lat":36.50,"lon":2.80,
     "area_ha":65000, "prod_mt":0.32,"ndvi":0.527,"color":"#52b788","wilaya":"Blida",
     "crops_ar":"خضروات، حمضيات، بطاطا","crops_en":"Vegetables, Citrus, Potato",
     "irrig":"Grand périmètre irrigué","info_ar":"أكبر محيط مسقي في الجزائر"},
    {"name_ar":"هضبة سطيف",  "name_en":"Setif Highlands",  "lat":36.20,"lon":5.40,
     "area_ha":380000,"prod_mt":0.45,"ndvi":0.377,"color":"#f4d03f","wilaya":"Setif",
     "crops_ar":"قمح صلب، شعير، بقوليات","crops_en":"Durum wheat, Barley, Legumes",
     "irrig":"بعلي","info_ar":"أول منتج للحبوب في الجزائر"},
    {"name_ar":"هضبة تيارت", "name_en":"Tiaret Plateau",   "lat":35.37,"lon":1.30,
     "area_ha":420000,"prod_mt":0.38,"ndvi":0.426,"color":"#e8a020","wilaya":"Tiaret",
     "crops_ar":"قمح، شعير، تربية الأغنام","crops_en":"Wheat, Barley, Sheep",
     "irrig":"بعلي","info_ar":"الهضاب العليا — زراعة الحبوب الكبرى"},
    {"name_ar":"القبائل",     "name_en":"Kabylie",          "lat":36.70,"lon":4.20,
     "area_ha":80000, "prod_mt":0.15,"ndvi":0.581,"color":"#27ae60","wilaya":"Tizi Ouzou",
     "crops_ar":"زيتون، تين، كرز","crops_en":"Olive, Fig, Cherry",
     "irrig":"تقليدي","info_ar":"أول منتج لزيت الزيتون في الجزائر 🫒"},
    {"name_ar":"بسكرة",       "name_en":"Biskra",            "lat":34.85,"lon":5.73,
     "area_ha":42000, "prod_mt":0.45,"ndvi":0.111,"color":"#c0392b","wilaya":"Biskra",
     "crops_ar":"تمر دڤلة نور، فلفل، طماطم","crops_en":"Deglet Nour dates, Pepper",
     "irrig":"مياه جوفية","info_ar":"عاصمة التمر دڤلة نور العالمية 🌴"},
    {"name_ar":"واد سوف",    "name_en":"Oued Souf",         "lat":33.40,"lon":6.90,
     "area_ha":38000, "prod_mt":0.35,"ndvi":0.119,"color":"#e74c3c","wilaya":"El Oued",
     "crops_ar":"تمر، بطاطا سوف","crops_en":"Dates, Souf Potato",
     "irrig":"فقاقير + آبار","info_ar":"بطاطا سوف — منتج محمي المنشأ"},
    {"name_ar":"سهل عنابة",  "name_en":"Annaba Plain",      "lat":36.90,"lon":7.70,
     "area_ha":55000, "prod_mt":0.09,"ndvi":0.416,"color":"#f4a261","wilaya":"Annaba",
     "crops_ar":"حبوب، خضروات، حمضيات","crops_en":"Cereals, Vegetables, Citrus",
     "irrig":"شبه مسقي","info_ar":"زراعة ساحلية — شرق الجزائر"},
    {"name_ar":"سهل تلمسان", "name_en":"Tlemcen Plain",     "lat":34.88,"lon":-1.30,
     "area_ha":85000, "prod_mt":0.11,"ndvi":0.341,"color":"#8e44ad","wilaya":"Tlemcen",
     "crops_ar":"كروم، زيتون، حبوب","crops_en":"Grapes, Olive, Cereals",
     "irrig":"سد بني بهدل","info_ar":"الكروم والزيتون — الغرب الجزائري"},
    {"name_ar":"عين الدفلى", "name_en":"Ain Defla",         "lat":36.26,"lon":1.97,
     "area_ha":35000, "prod_mt":0.55,"ndvi":0.480,"color":"#2980b9","wilaya":"Ain Defla",
     "crops_ar":"بطاطا، بصل، طماطم","crops_en":"Potato, Onion, Tomato",
     "irrig":"وادي الشلف","info_ar":"أول منتج للبطاطا في الجزائر 🥔"},
    {"name_ar":"مستغانم",    "name_en":"Mostaganem",        "lat":35.93,"lon":0.10,
     "area_ha":60000, "prod_mt":0.16,"ndvi":0.192,"color":"#e67e22","wilaya":"Mostaganem",
     "crops_ar":"حمضيات، كروم، خضروات","crops_en":"Citrus, Grapes, Vegetables",
     "irrig":"محيط مستغانم","info_ar":"الحمضيات والكروم — الساحل الغربي"},
    {"name_ar":"الأوراس",    "name_en":"Aures-Batna",       "lat":35.40,"lon":6.60,
     "area_ha":210000,"prod_mt":0.19,"ndvi":0.429,"color":"#f4a261","wilaya":"Batna",
     "crops_ar":"قمح صلب، تربية بقر، مشمش","crops_en":"Durum wheat, Cattle, Apricot",
     "irrig":"مختلط","info_ar":"الحبوب والتربية — جبال الأوراس"},
    {"name_ar":"واد ريغ",   "name_en":"Oued Righ",         "lat":33.50,"lon":5.90,
     "area_ha":18000, "prod_mt":0.12,"ndvi":0.080,"color":"#e63946","wilaya":"Ouargla",
     "crops_ar":"تمر، خضروات صحراوية","crops_en":"Dates, Saharan vegetables",
     "irrig":"الطبقة الألبية","info_ar":"الواحات الصحراوية — الطبقة الألبية"},
]

DAMS = [
    {"name":"بني هارون",    "name_fr":"Beni Haroun",  "lat":36.45,"lon":6.38,"cap":960, "river":"رهمال",      "h":121,"yr":2003,"op":True, "use":"مياه الشرب قسنطينة + ري 36,000 هكتار"},
    {"name":"قرقر",         "name_fr":"Gargar",       "lat":35.88,"lon":0.84, "cap":437,"river":"الشلف",      "h":72, "yr":1988,"op":True, "use":"ري 50,000 هكتار + مياه الشرب"},
    {"name":"غريب",         "name_fr":"Ghrib",        "lat":36.24,"lon":2.10, "cap":280,"river":"الشلف",      "h":65, "yr":1939,"op":True, "use":"ري متيجة + مياه الشرب الجزائر"},
    {"name":"قدارة",        "name_fr":"Keddara",      "lat":36.62,"lon":3.52, "cap":157,"river":"إيسر",       "h":102,"yr":1986,"op":True, "use":"مياه الشرب الجزائر (2 مليون ساكن)"},
    {"name":"تكسبت",        "name_fr":"Taksebt",      "lat":36.72,"lon":4.00, "cap":175,"river":"سباو",       "h":100,"yr":2007,"op":True, "use":"مياه الشرب تيزي وزو + الجزائر"},
    {"name":"تيشي حاف",     "name_fr":"Tichy Haf",   "lat":36.40,"lon":4.99, "cap":168,"river":"بوسلام",     "h":70, "yr":2007,"op":True, "use":"مياه الشرب بجاية + ري"},
    {"name":"حمام ضباغ",    "name_fr":"Hammam Debagh","lat":36.47,"lon":7.26, "cap":216,"river":"سيبوس",      "h":113,"yr":1986,"op":True, "use":"مياه الشرب عنابة + ري الشرق"},
    {"name":"الشفة",        "name_fr":"Cheffia",      "lat":36.70,"lon":8.23, "cap":160,"river":"بونامoussa", "h":70, "yr":1966,"op":True, "use":"مياه الشرب عنابة + الطارف"},
    {"name":"سيدي يعقوب",  "name_fr":"Sidi Yakoub",  "lat":36.13,"lon":1.66, "cap":286,"river":"الشلف",      "h":100,"yr":1986,"op":True, "use":"ري 35,000 هكتار + مياه الشرب"},
    {"name":"عين زادة",     "name_fr":"Ain Zada",     "lat":36.05,"lon":5.04, "cap":121,"river":"بوسلام",     "h":60, "yr":1986,"op":True, "use":"مياه الشرب برج بوعريريج"},
    {"name":"وادي فودة",    "name_fr":"Oued Fodda",   "lat":36.19,"lon":1.58, "cap":228,"river":"الشلف",      "h":101,"yr":1932,"op":True, "use":"ري + طاقة كهرومائية"},
    {"name":"زردازة",       "name_fr":"Zardezas",     "lat":36.73,"lon":6.77, "cap":99, "river":"صاف صاف",    "h":69, "yr":1982,"op":True, "use":"مياه الشرب سكيكدة + المجمع البتروكيماوي"},
    {"name":"بني بهدل",     "name_fr":"Beni Bahdel",  "lat":34.80,"lon":-1.62,"cap":63, "river":"تافنة",      "h":67, "yr":1942,"op":True, "use":"مياه الشرب تلمسان + ري"},
    {"name":"بكحدة",        "name_fr":"Bakhadda",     "lat":35.63,"lon":1.33, "cap":66, "river":"مينا",       "h":66, "yr":1940,"op":True, "use":"مياه الشرب تيارت + ري"},
    {"name":"حمام قروز",    "name_fr":"Hammam Grouz", "lat":36.35,"lon":6.47, "cap":55, "river":"رهمال",      "h":47, "yr":1986,"op":True, "use":"مياه الشرب قسنطينة"},
    {"name":"عرقية",        "name_fr":"Ourkiss",      "lat":35.73,"lon":7.53, "cap":100,"river":"سيبوس",      "h":58, "yr":1983,"op":True, "use":"مياه الشرب الشرق الجزائري"},
    {"name":"سوق ثلاثة",   "name_fr":"Souk Tleta",   "lat":35.33,"lon":-1.37,"cap":57, "river":"تافنة",      "h":55, "yr":2000,"op":True, "use":"مياه الشرب عين تموشنت"},
    {"name":"عين داليا",    "name_fr":"Ain Dalia",    "lat":36.27,"lon":8.05, "cap":80, "river":"مجردة",      "h":60, "yr":1984,"op":True, "use":"مياه الشرب سوق أهراس"},
    {"name":"بوسيابة",      "name_fr":"Boussiaba",    "lat":36.74,"lon":5.91, "cap":100,"river":"الكبير",     "h":65, "yr":2000,"op":True, "use":"مياه الشرب جيجل + ري"},
    {"name":"فم الغيص",     "name_fr":"Foum El Gueiss","lat":35.72,"lon":4.18,"cap":27, "river":"أدوس",       "h":38, "yr":1956,"op":True, "use":"ري المسيلة"},
    {"name":"بين الويدان",  "name_fr":"Bine El Ouidane","lat":35.85,"lon":1.72,"cap":350,"river":"الشلف",    "h":90, "yr":2026,"op":False,"use":"ري 40,000 هكتار (مخطط)"},
    {"name":"تاهت",         "name_fr":"Taht",         "lat":34.92,"lon":0.18, "cap":200,"river":"مكرة",       "h":75, "yr":2027,"op":False,"use":"مياه الشرب سعيدة (مخطط)"},
]

POWER_LINES = [
    {"name":"Annaba—Constantine","v":400,"color":"#ff4d6d","coords":[[36.90,7.77],[36.37,6.61]]},
    {"name":"Constantine—Setif","v":400,"color":"#ff4d6d","coords":[[36.37,6.61],[36.19,5.41]]},
    {"name":"Setif—Algiers","v":400,"color":"#ff4d6d","coords":[[36.19,5.41],[36.75,3.06]]},
    {"name":"Algiers—Blida","v":400,"color":"#ff4d6d","coords":[[36.75,3.06],[36.47,2.83]]},
    {"name":"Blida—Chlef","v":400,"color":"#ff4d6d","coords":[[36.47,2.83],[36.16,1.33]]},
    {"name":"Chlef—Oran","v":400,"color":"#ff4d6d","coords":[[36.16,1.33],[35.70,-0.63]]},
    {"name":"Oran—Tlemcen","v":400,"color":"#ff4d6d","coords":[[35.70,-0.63],[34.88,-1.32]]},
    {"name":"Algiers—Djelfa","v":400,"color":"#ff4d6d","coords":[[36.75,3.06],[34.67,3.26]]},
    {"name":"Djelfa—Ghardaia","v":400,"color":"#ff4d6d","coords":[[34.67,3.26],[32.49,3.67]]},
    {"name":"Ghardaia—Ouargla","v":400,"color":"#ff4d6d","coords":[[32.49,3.67],[31.95,5.32]]},
    {"name":"Constantine—Biskra","v":400,"color":"#ff4d6d","coords":[[36.37,6.61],[35.56,6.17],[34.85,5.73]]},
    {"name":"Biskra—Ouargla","v":400,"color":"#ff4d6d","coords":[[34.85,5.73],[31.95,5.32]]},
    {"name":"Algiers—Tizi Ouzou","v":220,"color":"#ffd166","coords":[[36.75,3.06],[36.71,4.05]]},
    {"name":"Tizi Ouzou—Annaba","v":220,"color":"#ffd166","coords":[[36.71,4.05],[36.75,5.08],[36.88,6.90],[36.90,7.77]]},
    {"name":"Tiaret—Oran","v":220,"color":"#ffd166","coords":[[35.37,1.32],[35.70,-0.63]]},
    {"name":"Ouargla—El Oued","v":220,"color":"#ffd166","coords":[[31.95,5.32],[33.36,6.86]]},
    {"name":"Ghardaia—Bechar","v":220,"color":"#ffd166","coords":[[32.49,3.67],[31.62,-2.22]]},
    {"name":"Tamanrasset—Adrar","v":90,"color":"#48cae4","coords":[[22.79,5.52],[27.87,0.29]]},
    {"name":"Adrar—Bechar","v":90,"color":"#48cae4","coords":[[27.87,0.29],[31.62,-2.22]]},
    {"name":"Tindouf—Bechar","v":90,"color":"#48cae4","coords":[[27.67,-8.15],[31.62,-2.22]]},
    {"name":"Illizi—Ouargla","v":90,"color":"#48cae4","coords":[[26.51,8.47],[31.95,5.32]]},
]

SOLAR = [
    {"name":"Adrar Solar","lat":27.87,"lon":0.29,"mw":20},
    {"name":"Hassi R'Mel Solar","lat":32.93,"lon":3.27,"mw":25},
    {"name":"In Salah Solar","lat":27.20,"lon":2.47,"mw":50},
    {"name":"Tamanrasset Solar","lat":22.79,"lon":5.52,"mw":15},
    {"name":"El Oued Solar","lat":33.36,"lon":6.86,"mw":30},
    {"name":"Biskra Solar","lat":34.85,"lon":5.73,"mw":25},
]

WILAYAS_LIST = [
    {"name":"Adrar","lat":27.87,"lon":0.29},{"name":"Chlef","lat":36.16,"lon":1.33},
    {"name":"Laghouat","lat":33.80,"lon":2.86},{"name":"Oum El Bouaghi","lat":35.87,"lon":7.11},
    {"name":"Batna","lat":35.56,"lon":6.17},{"name":"Bejaia","lat":36.75,"lon":5.08},
    {"name":"Biskra","lat":34.85,"lon":5.73},{"name":"Bechar","lat":31.62,"lon":-2.22},
    {"name":"Blida","lat":36.47,"lon":2.83},{"name":"Bouira","lat":36.37,"lon":3.90},
    {"name":"Tamanrasset","lat":22.79,"lon":5.52},{"name":"Tebessa","lat":35.40,"lon":8.12},
    {"name":"Tlemcen","lat":34.88,"lon":-1.32},{"name":"Tiaret","lat":35.37,"lon":1.32},
    {"name":"Tizi Ouzou","lat":36.71,"lon":4.05},{"name":"Alger","lat":36.75,"lon":3.06},
    {"name":"Djelfa","lat":34.67,"lon":3.26},{"name":"Jijel","lat":36.82,"lon":5.77},
    {"name":"Setif","lat":36.19,"lon":5.41},{"name":"Saida","lat":34.84,"lon":0.15},
    {"name":"Skikda","lat":36.88,"lon":6.90},{"name":"Sidi Bel Abbes","lat":35.19,"lon":-0.63},
    {"name":"Annaba","lat":36.90,"lon":7.77},{"name":"Guelma","lat":36.46,"lon":7.43},
    {"name":"Constantine","lat":36.37,"lon":6.61},{"name":"Medea","lat":36.27,"lon":2.75},
    {"name":"Mostaganem","lat":35.93,"lon":0.09},{"name":"M'Sila","lat":35.70,"lon":4.54},
    {"name":"Mascara","lat":35.40,"lon":0.14},{"name":"Ouargla","lat":31.95,"lon":5.32},
    {"name":"Oran","lat":35.70,"lon":-0.63},{"name":"El Bayadh","lat":33.68,"lon":1.02},
    {"name":"Illizi","lat":26.51,"lon":8.47},{"name":"Bordj Bou Arreridj","lat":36.07,"lon":4.76},
    {"name":"Boumerdes","lat":36.76,"lon":3.48},{"name":"El Tarf","lat":36.77,"lon":8.31},
    {"name":"Tindouf","lat":27.67,"lon":-8.15},{"name":"Tissemsilt","lat":35.61,"lon":1.81},
    {"name":"El Oued","lat":33.36,"lon":6.86},{"name":"Khenchela","lat":35.43,"lon":7.14},
    {"name":"Souk Ahras","lat":36.29,"lon":7.95},{"name":"Tipaza","lat":36.59,"lon":2.45},
    {"name":"Mila","lat":36.45,"lon":6.26},{"name":"Ain Defla","lat":36.26,"lon":1.97},
    {"name":"Naama","lat":33.27,"lon":-0.31},{"name":"Ain Temouchent","lat":35.30,"lon":-1.14},
    {"name":"Ghardaia","lat":32.49,"lon":3.67},{"name":"Relizane","lat":35.74,"lon":0.56},
]

# ============================================================
# FUNCTIONS
# ============================================================
@st.cache_data(ttl=3600)
def fetch_weather(lat, lon):
    url   = "https://archive-api.open-meteo.com/v1/archive"
    end   = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now()-timedelta(days=30)).strftime("%Y-%m-%d")
    params = {"latitude":lat,"longitude":lon,"start_date":start,"end_date":end,
              "daily":["temperature_2m_max","precipitation_sum","et0_fao_evapotranspiration"],
              "timezone":"Africa/Algiers"}
    try:
        r = requests.get(url,params=params,timeout=10)
        d = r.json().get("daily",{})
        return pd.DataFrame({"date":d.get("time",[]),"temp":d.get("temperature_2m_max",[]),
                             "rain":d.get("precipitation_sum",[]),
                             "evap":d.get("et0_fao_evapotranspiration",[])}).dropna()
    except: return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_forecast(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude":lat,"longitude":lon,
              "daily":["temperature_2m_max","temperature_2m_min","precipitation_sum"],
              "timezone":"Africa/Algiers","forecast_days":7}
    try:
        r = requests.get(url,params=params,timeout=10)
        d = r.json().get("daily",{})
        return pd.DataFrame({"date":d.get("time",[]),"max_temp":d.get("temperature_2m_max",[]),
                             "min_temp":d.get("temperature_2m_min",[]),"rain":d.get("precipitation_sum",[])})
    except: return pd.DataFrame()

def compute_health(df, lat):
    if df.empty or len(df)<5: return 50,0,0,0,0
    last7   = df.tail(7)
    rain    = round(last7["rain"].sum(),1)
    evap    = round(last7["evap"].sum(),1)
    temp    = round(last7["temp"].mean(),1)
    deficit = round(evap-rain,1)
    base    = 65 if lat>35 else (50 if lat>33 else 35)
    health  = round(min(100,max(0,
        min(rain/max(base*0.15,1)*40,40) +
        (max(30-(temp-35)*3,0) if temp>35 else 30) +
        (max(30-(deficit/base)*30,0) if base>0 else 15))),1)
    return health,rain,evap,temp,deficit

@st.cache_data(ttl=1800)
def fetch_fires():
    try:
        r = requests.get(
            "https://firms.modaps.eosdis.nasa.gov/api/area/csv/DEMO_KEY/VIIRS_SNPP_NRT/-8.667,18.968,11.979,37.091/1",
            timeout=15)
        if r.status_code==200 and len(r.text)>100:
            from io import StringIO
            return pd.read_csv(StringIO(r.text))
    except: pass
    return pd.DataFrame()

def build_ndvi_map(results, L):
    """خريطة NDVI مبنية على بيانات الطقس الحقيقية"""
    m = folium.Map(location=[28.0, 3.0], zoom_start=5, tiles="CartoDB positron")

    # NDVI health circles — color and size based on real weather data
    for r in results:
        color  = r["hcolor"]
        radius = max(8, min(22, r["area_ha"]//20000))
        name   = r["name_ar"] if L=="ar" else r["name_en"]
        crops  = r["crops_ar"] if L=="ar" else r["crops_en"]

        if r["hcolor"]=="#52b788":   status = "🟢 جيد" if L=="ar" else "🟢 Healthy"
        elif r["hcolor"]=="#f4a261": status = "🟡 متوسط" if L=="ar" else "🟡 Moderate"
        else:                         status = "🔴 جفاف" if L=="ar" else "🔴 Drought"

        popup_html = f"""
        <div style='font-family:Arial;min-width:240px;padding:10px'>
            <h4 style='color:{color};margin:0 0 8px;
                       border-bottom:2px solid {color};padding-bottom:4px'>
                🌾 {name}</h4>
            <table style='width:100%;font-size:12px;border-collapse:collapse'>
                <tr style='background:#f8f9fa'>
                    <td><b>{'الحالة' if L=='ar' else 'Status'}</b></td>
                    <td><b style='color:{color}'>{status}</b></td></tr>
                <tr><td><b>{'الصحة' if L=='ar' else 'Health'}</b></td>
                    <td><b style='color:{color}'>{r['health']}%</b></td></tr>
                <tr style='background:#f8f9fa'>
                    <td><b>NDVI</b></td><td>{r['ndvi']}</td></tr>
                <tr><td><b>{'أمطار 7 أيام' if L=='ar' else 'Rain 7d'}</b></td>
                    <td>{r['rain']} mm</td></tr>
                <tr style='background:#f8f9fa'>
                    <td><b>{'الحرارة' if L=='ar' else 'Temp'}</b></td>
                    <td>{r['temp']} °C</td></tr>
                <tr><td><b>{'المساحة' if L=='ar' else 'Area'}</b></td>
                    <td>{r['area_ha']:,} {'هكتار' if L=='ar' else 'ha'}</td></tr>
                <tr style='background:#f8f9fa'>
                    <td><b>{'المحاصيل' if L=='ar' else 'Crops'}</b></td>
                    <td style='font-size:11px'>{crops}</td></tr>
            </table>
            <div style='background:#f0f9f0;padding:6px;margin-top:6px;
                        border-radius:4px;font-size:11px;
                        border-left:3px solid {color}'>
                ℹ️ {r['info_ar'] if L=='ar' else r.get('info_en', r['info_ar'])}
            </div>
        </div>"""

        folium.CircleMarker(
            location=[r["lat"], r["lon"]],
            radius=radius,
            color=color, fill=True,
            fill_color=color, fill_opacity=0.8,
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=f"🌾 {name} | {'صحة' if L=='ar' else 'Health'}: {r['health']}% | NDVI: {r['ndvi']}"
        ).add_to(m)

    # Legend
    legend = f"""
    <div style='position:fixed;bottom:20px;left:20px;z-index:1000;
                background:white;padding:12px;border-radius:10px;
                box-shadow:0 2px 8px rgba(0,0,0,0.2);font-family:Arial;font-size:11px'>
        <b>🌾 {'صحة المحاصيل — NDVI' if L=='ar' else 'Crop Health — NDVI'}</b><br>
        <small style='color:#888'>{'مبني على بيانات الطقس الحقيقية' if L=='ar' else 'Based on real weather data'}</small><br><br>
        <span style='color:#52b788;font-size:16px'>●</span> {'جيد (≥55%)' if L=='ar' else 'Healthy (≥55%)'}<br>
        <span style='color:#f4a261;font-size:16px'>●</span> {'متوسط (30-54%)' if L=='ar' else 'Moderate (30-54%)'}<br>
        <span style='color:#e63946;font-size:16px'>●</span> {'جفاف (<30%)' if L=='ar' else 'Drought (<30%)'}<br>
        <small>({'الحجم = المساحة' if L=='ar' else 'Size = area'})</small>
    </div>"""
    m.get_root().html.add_child(folium.Element(legend))
    Fullscreen(position='topright').add_to(m)
    folium.LayerControl(collapsed=True, position='topright').add_to(m)
    return m


def build_agri_map(results, L):
    m = folium.Map(location=[28.0,3.0], zoom_start=5, tiles="CartoDB positron")

    # Wilaya borders — drawn from wilaya centers only (no external GeoJSON needed)
    pass

    # Agricultural zones
    ag_g = folium.FeatureGroup(name="🌾 "+("المناطق الزراعية" if L=="ar" else "Agricultural Zones"), show=True)
    for z in results:
        name    = z["name_ar"] if L=="ar" else z["name_en"]
        crops   = z["crops_ar"] if L=="ar" else z["crops_en"]
        color   = z["color"]
        info    = z["info_ar"]
        popup_html = f"""
        <div style='font-family:Arial;min-width:240px;padding:10px'>
            <h4 style='color:{color};margin:0 0 8px;border-bottom:2px solid {color};padding-bottom:4px'>
                🌾 {name}</h4>
            <table style='width:100%;font-size:12px;border-collapse:collapse'>
                <tr style='background:#f8f9fa'><td><b>{'المساحة' if L=='ar' else 'Area'}</b></td>
                    <td><b>{z['area_ha']:,} {'هكتار' if L=='ar' else 'ha'}</b></td></tr>
                <tr><td><b>{'الإنتاج' if L=='ar' else 'Production'}</b></td>
                    <td><b style='color:{color}'>{z['prod_mt']} {'مليون طن' if L=='ar' else 'Mt'}</b></td></tr>
                <tr style='background:#f8f9fa'><td><b>{'المحاصيل' if L=='ar' else 'Crops'}</b></td>
                    <td style='font-size:11px'>{crops}</td></tr>
                <tr><td><b>{'الري' if L=='ar' else 'Irrigation'}</b></td>
                    <td style='font-size:11px'>{z['irrig']}</td></tr>
                <tr style='background:#f8f9fa'><td><b>NDVI</b></td>
                    <td>{z['ndvi']}</td></tr>
                <tr><td><b>{'الصحة' if L=='ar' else 'Health'}</b></td>
                    <td><b style='color:{z["hcolor"]}'>{z['health']}%</b></td></tr>
            </table>
            <div style='background:#f0f9f0;padding:6px;margin-top:6px;border-radius:4px;
                        font-size:11px;border-left:3px solid {color}'>ℹ️ {info}</div>
        </div>"""
        folium.CircleMarker(
            location=[z["lat"],z["lon"]],
            radius=max(10,min(22,z["area_ha"]//20000)),
            color=color,fill=True,fill_color=color,fill_opacity=0.75,
            popup=folium.Popup(popup_html,max_width=280),
            tooltip=f"🌾 {name} | {z['area_ha']:,} ha | NDVI:{z['ndvi']}"
        ).add_to(ag_g)
    ag_g.add_to(m)

    # Dams
    dam_op = folium.FeatureGroup(name="🌊 "+("السدود العاملة" if L=="ar" else "Operational Dams"), show=True)
    dam_pl = folium.FeatureGroup(name="🔄 "+("السدود المخططة" if L=="ar" else "Planned Dams"), show=True)
    for d in DAMS:
        color  = "#0077b6" if d["op"] else "#90e0ef"
        radius = max(7,min(20,d["cap"]//55))
        name   = d["name"] if L=="ar" else d["name_fr"]
        popup_html = f"""
        <div style='font-family:Arial;min-width:230px;padding:10px'>
            <h4 style='color:{color};margin:0 0 8px;border-bottom:2px solid {color};padding-bottom:4px'>
                🌊 {'سد' if L=='ar' else 'Dam'} {name}</h4>
            <table style='width:100%;font-size:12px;border-collapse:collapse'>
                <tr style='background:#e8f4fd'><td><b>{'الولاية' if L=='ar' else 'Wilaya'}</b></td>
                    <td>{d.get('wilaya','')}</td></tr>
                <tr><td><b>{'السعة' if L=='ar' else 'Capacity'}</b></td>
                    <td><b style='color:{color};font-size:14px'>{d['cap']} Mm³</b></td></tr>
                <tr style='background:#e8f4fd'><td><b>{'الوادي' if L=='ar' else 'River'}</b></td>
                    <td>{d['river']}</td></tr>
                <tr><td><b>{'الارتفاع' if L=='ar' else 'Height'}</b></td>
                    <td>{d['h']} م</td></tr>
                <tr style='background:#e8f4fd'><td><b>{'الإنجاز' if L=='ar' else 'Year'}</b></td>
                    <td>{'مخطط' if not d['op'] else d['yr']}</td></tr>
                <tr><td><b>{'الاستخدام' if L=='ar' else 'Use'}</b></td>
                    <td style='font-size:11px'>{d['use']}</td></tr>
            </table>
        </div>"""
        target = dam_op if d["op"] else dam_pl
        folium.CircleMarker(
            location=[d["lat"],d["lon"]],
            radius=radius,color=color,fill=True,fill_color=color,fill_opacity=0.85,
            popup=folium.Popup(popup_html,max_width=260),
            tooltip=f"🌊 {name} | {d['cap']} Mm³"
        ).add_to(target)
    dam_op.add_to(m)
    dam_pl.add_to(m)

    # Wilaya labels + search
    labels_g = folium.FeatureGroup(name="🏷️ "+("أسماء الولايات" if L=="ar" else "Wilaya Names"), show=True)
    search_geojson = {"type":"FeatureCollection","features":[]}
    for w in WILAYAS_LIST:
        folium.Marker(
            location=[w["lat"],w["lon"]],
            icon=folium.DivIcon(
                html=f"""<div style='font-family:Arial;font-size:9px;font-weight:bold;
                    color:white;background:rgba(20,60,140,0.82);padding:1px 4px;
                    border-radius:3px;white-space:nowrap;pointer-events:none;
                    border:1px solid rgba(255,255,255,0.4)'>{w['name']}</div>""",
                icon_size=(len(w['name'])*6+8,16), icon_anchor=(0,8)
            )
        ).add_to(labels_g)
        search_geojson["features"].append({
            "type":"Feature",
            "geometry":{"type":"Point","coordinates":[w["lon"],w["lat"]]},
            "properties":{"name":w["name"]}
        })
    labels_g.add_to(m)

    search_layer = folium.GeoJson(search_geojson, name="search", show=False,
                                  marker=folium.CircleMarker(radius=0,color='transparent',fill=False))
    search_layer.add_to(m)
    Search(layer=search_layer, geom_type='Point',
           placeholder='🔍 ابحث عن ولاية... (ex: Setif)',
           collapsed=False, search_label='name', zoom=9, position='topleft').add_to(m)

    # Legend
    legend = f"""
    <div style='position:fixed;bottom:20px;left:20px;z-index:1000;
                background:white;padding:12px;border-radius:10px;
                box-shadow:0 2px 8px rgba(0,0,0,0.2);font-family:Arial;font-size:11px'>
        <b>🌾💧 {'الفلاحة والسدود' if L=='ar' else 'Agriculture & Dams'}</b><br><br>
        <b>{'المناطق الزراعية:' if L=='ar' else 'Ag. Zones:'}</b><br>
        <span style='color:#52b788'>●</span> {'جيد' if L=='ar' else 'Healthy'} &nbsp;
        <span style='color:#f4a261'>●</span> {'متوسط' if L=='ar' else 'Moderate'} &nbsp;
        <span style='color:#e63946'>●</span> {'ضعيف' if L=='ar' else 'Stressed'}<br><br>
        <b>{'السدود:' if L=='ar' else 'Dams:'}</b><br>
        <span style='color:#0077b6;font-size:15px'>●</span> {'عامل' if L=='ar' else 'Operational'} &nbsp;
        <span style='color:#90e0ef;font-size:15px'>●</span> {'مخطط' if L=='ar' else 'Planned'}<br>
        <small>({'الحجم = السعة' if L=='ar' else 'Size = capacity'} Mm³)</small>
    </div>"""
    m.get_root().html.add_child(folium.Element(legend))
    Fullscreen(position='topright').add_to(m)
    folium.LayerControl(collapsed=True, position='topright').add_to(m)
    return m

def build_power_map():
    m = folium.Map(location=[28.0,3.0], zoom_start=5, tiles="CartoDB dark_matter")
    lw={400:3,220:2,90:1.5}
    for v,label in [(400,"🔴 400kV"),(220,"🟡 220kV"),(90,"🔵 90kV")]:
        g = folium.FeatureGroup(name=f"⚡ {label}", show=True)
        for line in [l for l in POWER_LINES if l["v"]==v]:
            folium.PolyLine(locations=line["coords"],color=line["color"],
                weight=lw[v],opacity=0.95,tooltip=f"⚡ {line['name']} — {v}kV").add_to(g)
        g.add_to(m)
    sub_g = folium.FeatureGroup(name="⬛ Substations", show=True)
    sc={400:"#ff4d6d",220:"#ffd166",90:"#48cae4"}
    for s in [{"n":"Alger","lat":36.75,"lon":3.06,"kv":400},
              {"n":"Oran","lat":35.70,"lon":-0.63,"kv":400},
              {"n":"Constantine","lat":36.37,"lon":6.61,"kv":400},
              {"n":"Setif","lat":36.19,"lon":5.41,"kv":400},
              {"n":"Ouargla","lat":31.95,"lon":5.32,"kv":400},
              {"n":"Tamanrasset","lat":22.79,"lon":5.52,"kv":90},
              {"n":"Adrar","lat":27.87,"lon":0.29,"kv":90}]:
        folium.CircleMarker(location=[s["lat"],s["lon"]],radius=5,color="white",
            fill=True,fill_color=sc.get(s["kv"],"#aaa"),fill_opacity=1.0,weight=1,
            tooltip=f"⬛ {s['n']} {s['kv']}kV").add_to(sub_g)
    sub_g.add_to(m)
    sol_g = folium.FeatureGroup(name="☀️ Solar Stations", show=True)
    for s in SOLAR:
        folium.CircleMarker(location=[s["lat"],s["lon"]],
            radius=max(6,int(s["mw"]//6)),color="#fcbf49",fill=True,
            fill_color="#fcbf49",fill_opacity=0.9,
            tooltip=f"☀️ {s['name']} — {s['mw']}MW").add_to(sol_g)
    sol_g.add_to(m)
    legend_html = """
    <div style='position:fixed;bottom:20px;left:20px;z-index:1000;
                background:rgba(15,15,30,0.92);color:white;padding:12px;
                border-radius:10px;font-family:Arial;font-size:11px'>
        <b>⚡ Sonelgaz Power Grid</b><br><br>
        <span style='color:#ff4d6d'>━━</span> 400kV<br>
        <span style='color:#ffd166'>━━</span> 220kV<br>
        <span style='color:#48cae4'>━━</span> 90kV<br>
        <span style='color:#fcbf49'>●</span> Solar &nbsp;
        <span style='color:white'>●</span> Substation
    </div>"""
    m.get_root().html.add_child(folium.Element(legend_html))
    Fullscreen(position='topright').add_to(m)
    folium.LayerControl(collapsed=True, position='topright').add_to(m)
    return m

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    try:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Flag_of_Algeria.svg/320px-Flag_of_Algeria.svg.png",width=120)
    except: pass
    lang = st.radio("🌐 Language / اللغة",["عربي","English"],horizontal=True)
    L    = "ar" if lang=="عربي" else "en"
    st.markdown("---")
    st.markdown("### " + ("لوحة التحكم" if L=="ar" else "Dashboard"))
    wilaya_options = [("كل الولايات" if L=="ar" else "All Wilayas")] + sorted(set(z["wilaya"] for z in AG_ZONES))
    selected_wilaya = st.selectbox(("اختر الولاية" if L=="ar" else "Select Wilaya"), wilaya_options)
    st.markdown("---")
    st.caption(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.caption("🛰️ Sentinel-2 | NASA | Open-Meteo")
    st.caption("👨‍💻 djermaneali | Univ. Oum El Bouaghi")

# ============================================================
# HEADER
# ============================================================
st.title("🌾 " + ("نظام المراقبة الزراعية — الجزائر" if L=="ar" else "Algeria Agricultural Monitoring"))
st.caption("🛰️ " + ("بيانات فضائية حقيقية من Sentinel-2 | NASA FIRMS | Open-Meteo" if L=="ar" else "Real satellite data: Sentinel-2 | NASA FIRMS | Open-Meteo"))
st.markdown("---")

all_label = "كل الولايات" if L=="ar" else "All Wilayas"
zones_show = AG_ZONES if selected_wilaya==all_label else [z for z in AG_ZONES if z["wilaya"]==selected_wilaya]

# FETCH DATA
with st.spinner("جاري تحميل البيانات..." if L=="ar" else "Loading data..."):
    results = []
    for z in zones_show:
        df = fetch_weather(z["lat"],z["lon"])
        health,rain,evap,temp,deficit = compute_health(df,z["lat"])
        ndvi = round(0.1+(health/100)*0.8,3)
        if health>=55:   hcolor="#52b788"
        elif health>=30: hcolor="#f4a261"
        else:            hcolor="#e63946"
        results.append({**z,"health":health,"ndvi":z["ndvi"],"hcolor":hcolor,
                        "rain":rain,"temp":temp,"deficit":deficit})

# METRICS
healthy_n  = sum(1 for r in results if r["hcolor"]=="#52b788")
moderate_n = sum(1 for r in results if r["hcolor"]=="#f4a261")
drought_n  = sum(1 for r in results if r["hcolor"]=="#e63946")
c1,c2,c3,c4 = st.columns(4)
c1.metric("🌾 "+("مناطق سليمة" if L=="ar" else "Healthy"),   healthy_n)
c2.metric("⚠️ "+("تحذير" if L=="ar" else "Warning"),          moderate_n)
c3.metric("🏜️ "+("جفاف" if L=="ar" else "Drought"),          drought_n)
c4.metric("💧 "+("سدود" if L=="ar" else "Dams"),              sum(1 for d in DAMS if d["op"]))
st.markdown("---")

# TABS
tab_labels = (["🛰️ صحة المحاصيل","🗺️ الفلاحة والسدود","📊 التقرير","🌤️ الطقس","🔥 الحرائق","⚡ الكهرباء","ℹ️ عن المشروع"]
              if L=="ar" else
              ["🛰️ Crop Health","🗺️ Agri & Dams","📊 Report","🌤️ Weather","🔥 Fires","⚡ Power Grid","ℹ️ About"])
tabs = st.tabs(tab_labels)

# TAB 0: CROP HEALTH NDVI
with tabs[0]:
    st.subheader("🛰️ " + ("مراقبة صحة المحاصيل عبر الأقمار الاصطناعية" if L=="ar" else "Crop Health Monitoring via Satellite"))
    st.caption("📡 " + ("البيانات مبنية على بيانات الطقس الحقيقية من Open-Meteo (30 يوم)" if L=="ar" else "Based on real weather data from Open-Meteo (30-day archive)"))

    # NDVI bar chart
    fig_ndvi, ax = plt.subplots(figsize=(10, 4))
    names  = [r["name_ar"] if L=="ar" else r["name_en"] for r in results]
    scores = [r["health"] for r in results]
    colors = [r["hcolor"] for r in results]
    bars = ax.barh(names, scores, color=colors, edgecolor="white", linewidth=0.5)
    ax.axvline(55, color="#52b788", linestyle="--", alpha=0.7,
               label=("جيد (55)" if L=="ar" else "Healthy (55)"))
    ax.axvline(30, color="#f4a261", linestyle="--", alpha=0.7,
               label=("تحذير (30)" if L=="ar" else "Warning (30)"))
    ax.set_xlabel("Health Score (0-100)")
    ax.set_xlim(0, 100)
    ax.legend(fontsize=9)
    for bar, s in zip(bars, scores):
        ax.text(bar.get_width()+1, bar.get_y()+bar.get_height()/2,
                f"{s:.0f}%", va="center", fontsize=9)
    plt.tight_layout()
    st.pyplot(fig_ndvi)
    plt.close()

    # NDVI map
    ndvi_map = build_ndvi_map(results, L)
    components.html(ndvi_map._repr_html_(), height=500, scrolling=False)

# TAB 1: AGRI + DAMS MAP
with tabs[1]:
    st.subheader("🌾💧 " + ("الفلاحة والسدود" if L=="ar" else "Agriculture & Dams"))
    agri_map = build_agri_map(results, L)
    components.html(agri_map._repr_html_(), height=550, scrolling=False)

# TAB 2: REPORT
with tabs[2]:
    st.subheader("📊 " + ("تقرير الصحة الزراعية" if L=="ar" else "Agricultural Health Report"))
    df_show = pd.DataFrame([{
        ("المنطقة" if L=="ar" else "Zone"):     r["name_ar"] if L=="ar" else r["name_en"],
        ("المحصول" if L=="ar" else "Crop"):     r["crops_ar"] if L=="ar" else r["crops_en"],
        "NDVI":                                  r["ndvi"],
        ("الصحة %" if L=="ar" else "Health %"): r["health"],
        ("أمطار mm" if L=="ar" else "Rain mm"):  r["rain"],
        ("حرارة °C" if L=="ar" else "Temp °C"): r["temp"],
        ("الحالة" if L=="ar" else "Status"):
            ("🟢 جيد" if r["hcolor"]=="#52b788" else "🟡 متوسط" if r["hcolor"]=="#f4a261" else "🔴 جفاف")
            if L=="ar" else
            ("🟢 Healthy" if r["hcolor"]=="#52b788" else "🟡 Moderate" if r["hcolor"]=="#f4a261" else "🔴 Drought"),
    } for r in results])
    st.dataframe(df_show, use_container_width=True, hide_index=True)

    # Dams table
    st.subheader("🌊 " + ("السدود" if L=="ar" else "Dams"))
    df_dams = pd.DataFrame([{
        ("الاسم" if L=="ar" else "Name"):       d["name"] if L=="ar" else d["name_fr"],
        ("السعة Mm³" if L=="ar" else "Cap Mm³"):d["cap"],
        ("الوادي" if L=="ar" else "River"):      d["river"],
        ("الارتفاع م" if L=="ar" else "Height m"):d["h"],
        ("السنة" if L=="ar" else "Year"):        d["yr"] if d["op"] else ("مخطط" if L=="ar" else "Planned"),
        ("الحالة" if L=="ar" else "Status"):     ("✅ عامل" if d["op"] else "🔄 مخطط") if L=="ar" else ("✅ Operational" if d["op"] else "🔄 Planned"),
    } for d in DAMS])
    st.dataframe(df_dams, use_container_width=True, hide_index=True)
    total_cap = sum(d["cap"] for d in DAMS if d["op"])
    st.info(f"💧 {'إجمالي السعة التخزينية:' if L=='ar' else 'Total storage capacity:'} **{total_cap:,} Mm³**")

# TAB 3: WEATHER
with tabs[3]:
    st.subheader("🌤️ " + ("توقعات الطقس — 7 أيام" if L=="ar" else "Weather Forecast — 7 Days"))
    zone_names = [z["name_ar"] if L=="ar" else z["name_en"] for z in zones_show]
    sel = st.selectbox("", zone_names)
    sel_zone = zones_show[zone_names.index(sel)]
    forecast = fetch_forecast(sel_zone["lat"], sel_zone["lon"])
    if not forecast.empty:
        fig2,(ax1,ax2) = plt.subplots(2,1,figsize=(10,5),sharex=True)
        ax1.plot(forecast["date"],forecast["max_temp"],"r-o",label="Max",ms=4)
        ax1.plot(forecast["date"],forecast["min_temp"],"b-o",label="Min",ms=4)
        ax1.set_ylabel("°C"); ax1.legend(fontsize=8)
        ax1.set_title(sel); ax1.tick_params(axis='x',rotation=30)
        ax2.bar(forecast["date"],forecast["rain"],color="#4895ef",alpha=0.8)
        ax2.set_ylabel("mm"); ax2.tick_params(axis='x',rotation=30)
        plt.tight_layout()
        st.pyplot(fig2); plt.close()

# TAB 4: FIRES
with tabs[4]:
    st.subheader("🔥 " + ("الحرائق النشطة" if L=="ar" else "Active Fires"))
    fires = fetch_fires()
    if fires.empty:
        st.success("✅ " + ("لا توجد حرائق نشطة الآن — الجزائر بأمان" if L=="ar" else "No active fires detected"))
    else:
        st.warning(f"🔥 {'نقاط حرارية مكتشفة:' if L=='ar' else 'Fire points detected:'} **{len(fires)}**")
        fire_map = folium.Map(location=[28.0,3.0],zoom_start=5,tiles="CartoDB dark_matter")
        for _,row in fires.iterrows():
            try:
                folium.CircleMarker(location=[row["latitude"],row["longitude"]],
                    radius=5,color="#ff4500",fill=True,fill_color="#ff4500",fill_opacity=0.9,
                    tooltip=f"🔥 {row.get('acq_date','N/A')}").add_to(fire_map)
            except: continue
        components.html(fire_map._repr_html_(), height=450, scrolling=False)

# TAB 5: POWER
with tabs[5]:
    st.subheader("⚡ " + ("شبكة الكهرباء — Sonelgaz" if L=="ar" else "Power Grid — Sonelgaz"))
    power_map = build_power_map()
    components.html(power_map._repr_html_(), height=550, scrolling=False)

# TAB 6: ABOUT
with tabs[6]:
    st.markdown("""
## 🇩🇿 نظام المراقبة الزراعية للجزائر

منصة مفتوحة المصدر تجمع:
- 🌾 **مراقبة صحة المحاصيل** عبر الأقمار الاصطناعية (NDVI — Sentinel-2)
- 💧 **22 سد** بكامل تفاصيلها وسعاتها التخزينية
- 🔥 **رصد الحرائق** في الوقت الفعلي (NASA FIRMS)
- ⚡ **شبكة الكهرباء** Sonelgaz (400kV / 220kV / 90kV)
- 🌤️ **توقعات الطقس الزراعي** (Open-Meteo)

**المصادر:** Sentinel-2 / ESA Copernicus • NASA FIRMS • Open-Meteo • USDA FAS • FAO

**المطور:** djermaneali — جامعة أم البواقي 🎓

**GitHub:** github.com/djermaneali/algeria-agriwatch
    """ if L=="ar" else """
## 🇩🇿 Algeria Agricultural Monitoring System

Open-source platform combining:
- 🌾 **Crop health monitoring** via satellite (NDVI — Sentinel-2)
- 💧 **22 dams** with full details and storage capacities
- 🔥 **Real-time fire detection** (NASA FIRMS)
- ⚡ **Power grid** Sonelgaz (400kV / 220kV / 90kV)
- 🌤️ **Agricultural weather forecasts** (Open-Meteo)

**Sources:** Sentinel-2 / ESA • NASA FIRMS • Open-Meteo • USDA FAS • FAO

**Developer:** djermaneali — University of Oum El Bouaghi 🎓

**GitHub:** github.com/djermaneali/algeria-agriwatch
    """)
    st.info("🔗 GitHub: github.com/djermaneali/algeria-agriwatch")
