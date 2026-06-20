import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from datetime import datetime, timedelta
import json

# ============================================================
#  CONFIG
# ============================================================
st.set_page_config(
    page_title="نظام المراقبة الزراعية — الجزائر | Algeria AgriWatch",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
#  TRANSLATIONS
# ============================================================
T = {
    "ar": {
        "title":        "🌾 نظام المراقبة الزراعية — الجزائر",
        "subtitle":     "بيانات فضائية حقيقية من Sentinel-2 | NASA FIRMS | Open-Meteo",
        "lang_label":   "اللغة / Language",
        "sidebar_title":"لوحة التحكم",
        "wilaya_select":"اختر الولاية",
        "all_wilayas":  "كل الولايات",
        "tab_map":      "🗺️ الخريطة",
        "tab_report":   "📊 التقرير",
        "tab_weather":  "🌤️ الطقس",
        "tab_fires":    "🔥 الحرائق",
        "tab_about":    "ℹ️ عن المشروع",
        "health_title": "صحة المحاصيل — NDVI",
        "weather_title":"توقعات الطقس — 7 أيام",
        "fire_title":   "الحرائق النشطة",
        "zone":         "المنطقة",
        "crop":         "المحصول",
        "ndvi":         "NDVI",
        "health":       "الصحة %",
        "rain":         "أمطار mm",
        "temp":         "حرارة °C",
        "deficit":      "عجز الماء mm",
        "status":       "الحالة",
        "healthy":      "🟢 جيد",
        "moderate":     "🟡 متوسط",
        "stressed":     "🔴 جفاف",
        "loading":      "جاري تحميل البيانات...",
        "no_fires":     "✅ لا توجد حرائق نشطة الآن",
        "fires_found":  "🔥 نقاط حرارية مكتشفة",
        "about_text":   """
## عن المشروع

**نظام المراقبة الزراعية للجزائر** هو منصة مفتوحة المصدر تهدف إلى:

- 🛰️ مراقبة صحة المحاصيل عبر الأقمار الاصطناعية
- 🔥 رصد الحرائق في الوقت الفعلي
- 🌤️ متابعة بيانات الطقس الزراعي
- 📊 إنتاج تقارير دورية للمناطق الزراعية

**المصادر:**
- Sentinel-2 / ESA Copernicus — صور فضائية
- NASA FIRMS — بيانات الحرائق
- Open-Meteo — بيانات الطقس

**المطور:** djermaneali — جامعة أم البواقي 🎓
        """,
        "metric_healthy": "مناطق سليمة",
        "metric_warning": "مناطق تحذير",
        "metric_drought": "مناطق جفاف",
        "last_update":  "آخر تحديث",
    },
    "en": {
        "title":        "🌾 Algeria Agricultural Monitoring System",
        "subtitle":     "Real satellite data from Sentinel-2 | NASA FIRMS | Open-Meteo",
        "lang_label":   "اللغة / Language",
        "sidebar_title":"Dashboard",
        "wilaya_select":"Select Wilaya",
        "all_wilayas":  "All Wilayas",
        "tab_map":      "🗺️ Map",
        "tab_report":   "📊 Report",
        "tab_weather":  "🌤️ Weather",
        "tab_fires":    "🔥 Fires",
        "tab_about":    "ℹ️ About",
        "health_title": "Crop Health — NDVI",
        "weather_title":"Weather Forecast — 7 Days",
        "fire_title":   "Active Fires",
        "zone":         "Zone",
        "crop":         "Crop",
        "ndvi":         "NDVI",
        "health":       "Health %",
        "rain":         "Rain mm",
        "temp":         "Temp °C",
        "deficit":      "Water Deficit mm",
        "status":       "Status",
        "healthy":      "🟢 Healthy",
        "moderate":     "🟡 Moderate",
        "stressed":     "🔴 Drought",
        "loading":      "Loading data...",
        "no_fires":     "✅ No active fires detected",
        "fires_found":  "🔥 Heat points detected",
        "about_text":   """
## About This Project

**Algeria Agricultural Monitoring System** is an open-source platform for:

- 🛰️ Monitoring crop health via satellite imagery
- 🔥 Real-time wildfire detection
- 🌤️ Agricultural weather tracking
- 📊 Periodic reports for agricultural zones

**Data Sources:**
- Sentinel-2 / ESA Copernicus — satellite imagery
- NASA FIRMS — fire data
- Open-Meteo — weather data

**Developer:** djermaneali — University of Oum El Bouaghi 🎓
        """,
        "metric_healthy": "Healthy Zones",
        "metric_warning": "Warning Zones",
        "metric_drought": "Drought Zones",
        "last_update":  "Last Update",
    }
}

# ============================================================
#  AGRICULTURAL ZONES DATA
# ============================================================
ZONES = [
    {"name_ar":"سهل متيجة",   "name_en":"Mitidja Plain",   "lat":36.5, "lon":2.8,  "crop_ar":"خضروات",    "crop_en":"Vegetables",    "wilaya":"Blida"},
    {"name_ar":"سهل عنابة",   "name_en":"Annaba Plain",    "lat":36.9, "lon":7.7,  "crop_ar":"حبوب",      "crop_en":"Cereals",        "wilaya":"Annaba"},
    {"name_ar":"واد سوف",     "name_en":"Oued Souf",       "lat":33.4, "lon":6.9,  "crop_ar":"تمور",      "crop_en":"Dates",          "wilaya":"El Oued"},
    {"name_ar":"سهل تلمسان",  "name_en":"Tlemcen Plain",   "lat":34.9, "lon":-1.3, "crop_ar":"عنب",       "crop_en":"Grapes",         "wilaya":"Tlemcen"},
    {"name_ar":"الأوراس",     "name_en":"Aures Mountains", "lat":35.4, "lon":6.6,  "crop_ar":"أشجار مثمرة","crop_en":"Fruit trees",   "wilaya":"Batna"},
    {"name_ar":"القبائل",     "name_en":"Kabylie",         "lat":36.7, "lon":4.2,  "crop_ar":"زيتون",     "crop_en":"Olives",         "wilaya":"Tizi Ouzou"},
    {"name_ar":"قسنطينة",     "name_en":"Constantine",     "lat":36.4, "lon":6.6,  "crop_ar":"حبوب",      "crop_en":"Cereals",        "wilaya":"Constantine"},
    {"name_ar":"هضبة تيارت", "name_en":"Tiaret Plateau",  "lat":35.4, "lon":1.3,  "crop_ar":"حبوب",      "crop_en":"Cereals",        "wilaya":"Tiaret"},
    {"name_ar":"هضبة سطيف",  "name_en":"Setif Highlands", "lat":36.2, "lon":5.4,  "crop_ar":"قمح",       "crop_en":"Wheat",          "wilaya":"Setif"},
    {"name_ar":"بسكرة",       "name_en":"Biskra",          "lat":34.8, "lon":5.7,  "crop_ar":"تمور وفلفل","crop_en":"Dates & pepper", "wilaya":"Biskra"},
    {"name_ar":"مستغانم",     "name_en":"Mostaganem",      "lat":35.9, "lon":0.1,  "crop_ar":"حمضيات",    "crop_en":"Citrus & vines", "wilaya":"Mostaganem"},
    {"name_ar":"واد ريغ",    "name_en":"Oued Righ",       "lat":33.5, "lon":5.9,  "crop_ar":"نخيل",      "crop_en":"Palms",          "wilaya":"Ouargla"},
]

# ============================================================
#  DATA FUNCTIONS
# ============================================================
@st.cache_data(ttl=3600)
def fetch_weather(lat, lon):
    url = "https://archive-api.open-meteo.com/v1/archive"
    end   = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    params = {
        "latitude": lat, "longitude": lon,
        "start_date": start, "end_date": end,
        "daily": ["temperature_2m_max","precipitation_sum","et0_fao_evapotranspiration"],
        "timezone": "Africa/Algiers"
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        d = r.json().get("daily", {})
        df = pd.DataFrame({
            "date": d.get("time",[]),
            "temp": d.get("temperature_2m_max",[]),
            "rain": d.get("precipitation_sum",[]),
            "evap": d.get("et0_fao_evapotranspiration",[])
        }).dropna()
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_forecast(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat, "longitude": lon,
        "daily": ["temperature_2m_max","temperature_2m_min","precipitation_sum"],
        "timezone": "Africa/Algiers", "forecast_days": 7
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        d = r.json().get("daily", {})
        return pd.DataFrame({
            "date":     d.get("time",[]),
            "max_temp": d.get("temperature_2m_max",[]),
            "min_temp": d.get("temperature_2m_min",[]),
            "rain":     d.get("precipitation_sum",[])
        })
    except:
        return pd.DataFrame()

def compute_health(df, lat):
    if df.empty or len(df) < 5:
        return 50, 0, 0, 0, 0
    last7 = df.tail(7)
    rain   = round(last7["rain"].sum(), 1)
    evap   = round(last7["evap"].sum(), 1)
    temp   = round(last7["temp"].mean(), 1)
    deficit= round(evap - rain, 1)
    base   = 65 if lat > 35 else (50 if lat > 33 else 35)
    rain_s = min(rain / max(base*0.15,1) * 40, 40)
    temp_s = max(30-(temp-35)*3, 0) if temp>35 else 30
    def_s  = max(30 - (deficit/base)*30, 0) if base>0 else 15
    health = round(min(100, max(0, rain_s+temp_s+def_s)), 1)
    return health, rain, evap, temp, deficit

@st.cache_data(ttl=1800)
def fetch_fires():
    bbox = "-8.667,18.968,11.979,37.091"
    url  = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/DEMO_KEY/VIIRS_SNPP_NRT/{bbox}/1"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200 and len(r.text) > 100:
            from io import StringIO
            return pd.read_csv(StringIO(r.text))
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# ============================================================
#  SIDEBAR
# ============================================================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Flag_of_Algeria.svg/320px-Flag_of_Algeria.svg.png", width=120)

    lang = st.radio("🌐 Language / اللغة", ["عربي", "English"], horizontal=True)
    L = "ar" if lang == "عربي" else "en"
    t = T[L]

    st.markdown("---")
    st.markdown(f"### {t['sidebar_title']}")

    wilaya_options = [t["all_wilayas"]] + sorted(set(z["wilaya"] for z in ZONES))
    selected_wilaya = st.selectbox(t["wilaya_select"], wilaya_options)

    st.markdown("---")
    st.caption(f"🕐 {t['last_update']}: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.caption("🛰️ Sentinel-2 | NASA | Open-Meteo")
    st.caption("👨‍💻 djermaneali | Univ. Oum El Bouaghi")

# ============================================================
#  HEADER
# ============================================================
st.title(t["title"])
st.caption(t["subtitle"])
st.markdown("---")

# Filter zones
if selected_wilaya != t["all_wilayas"]:
    zones_show = [z for z in ZONES if z["wilaya"] == selected_wilaya]
else:
    zones_show = ZONES

# ============================================================
#  FETCH ALL DATA
# ============================================================
with st.spinner(t["loading"]):
    results = []
    for z in zones_show:
        df = fetch_weather(z["lat"], z["lon"])
        health, rain, evap, temp, deficit = compute_health(df, z["lat"])
        ndvi = round(0.1 + (health/100)*0.8, 3)
        if health >= 55:   status = t["healthy"];  color = "#52b788"
        elif health >= 30: status = t["moderate"]; color = "#f4a261"
        else:              status = t["stressed"];  color = "#e63946"
        results.append({
            "name":    z["name_ar"] if L=="ar" else z["name_en"],
            "crop":    z["crop_ar"] if L=="ar" else z["crop_en"],
            "wilaya":  z["wilaya"],
            "lat":     z["lat"], "lon": z["lon"],
            "health":  health, "ndvi": ndvi,
            "rain":    rain, "temp": temp, "deficit": deficit,
            "status":  status, "color": color,
        })

# ============================================================
#  METRICS ROW
# ============================================================
healthy_n  = sum(1 for r in results if "🟢" in r["status"])
moderate_n = sum(1 for r in results if "🟡" in r["status"])
drought_n  = sum(1 for r in results if "🔴" in r["status"])

c1, c2, c3, c4 = st.columns(4)
c1.metric("🌾 " + t["metric_healthy"], healthy_n,  delta=None)
c2.metric("⚠️ " + t["metric_warning"], moderate_n, delta=None)
c3.metric("🏜️ " + t["metric_drought"], drought_n,  delta=None)
c4.metric("📍 Zones", len(results), delta=None)

st.markdown("---")

# ============================================================
#  TABS
# ============================================================
tabs = st.tabs([t["tab_map"], t["tab_report"], t["tab_weather"], t["tab_fires"], t["tab_about"]])

# ─── TAB 1: MAP ───
with tabs[0]:
    st.subheader(t["health_title"])

    m = folium.Map(location=[28.0, 3.0], zoom_start=5, tiles="CartoDB positron")

    for r in results:
        popup_html = f"""
        <div style='font-family:Arial;min-width:200px;padding:8px'>
            <h4 style='color:{r["color"]};margin:0 0 8px'>{r["name"]}</h4>
            <table style='font-size:12px;width:100%'>
                <tr><td><b>{t['crop']}</b></td><td>{r['crop']}</td></tr>
                <tr style='background:#f5f5f5'><td><b>{t['health']}</b></td>
                    <td><b style='color:{r["color"]}'>{r['health']}%</b></td></tr>
                <tr><td><b>{t['ndvi']}</b></td><td>{r['ndvi']}</td></tr>
                <tr style='background:#f5f5f5'><td><b>{t['rain']}</b></td><td>{r['rain']} mm</td></tr>
                <tr><td><b>{t['temp']}</b></td><td>{r['temp']} °C</td></tr>
                <tr style='background:#f5f5f5'><td><b>{t['deficit']}</b></td><td>{r['deficit']} mm</td></tr>
            </table>
        </div>"""
        folium.CircleMarker(
            location=[r["lat"], r["lon"]],
            radius=max(8, int(r["health"]/7)),
            color=r["color"], fill=True,
            fill_color=r["color"], fill_opacity=0.8,
            popup=folium.Popup(popup_html, max_width=240),
            tooltip=f"{r['name']} | {r['health']}%"
        ).add_to(m)

    # Legend
    legend = f"""
    <div style='position:fixed;bottom:20px;left:20px;z-index:1000;
                background:white;padding:12px;border-radius:8px;
                box-shadow:0 2px 8px rgba(0,0,0,0.2);font-size:12px;font-family:Arial'>
        <b>{t['health_title']}</b><br><br>
        <span style='color:#52b788'>&#9679;</span> {t['healthy']}<br>
        <span style='color:#f4a261'>&#9679;</span> {t['moderate']}<br>
        <span style='color:#e63946'>&#9679;</span> {t['stressed']}
    </div>"""
    m.get_root().html.add_child(folium.Element(legend))

    st_folium(m, width=None, height=500, returned_objects=[])

# ─── TAB 2: REPORT ───
with tabs[1]:
    st.subheader(t["health_title"])

    df_show = pd.DataFrame([{
        t["zone"]:    r["name"],
        t["crop"]:    r["crop"],
        t["ndvi"]:    r["ndvi"],
        t["health"]:  r["health"],
        t["rain"]:    r["rain"],
        t["temp"]:    r["temp"],
        t["deficit"]: r["deficit"],
        t["status"]:  r["status"],
    } for r in results])

    st.dataframe(df_show, use_container_width=True, hide_index=True)

    # Bar chart
    fig, ax = plt.subplots(figsize=(10, 4))
    names  = [r["name"] for r in results]
    scores = [r["health"] for r in results]
    colors = [r["color"] for r in results]
    bars = ax.barh(names, scores, color=colors, edgecolor="white", linewidth=0.5)
    ax.axvline(55, color="#52b788", linestyle="--", alpha=0.6, label="55")
    ax.axvline(30, color="#f4a261", linestyle="--", alpha=0.6, label="30")
    ax.set_xlabel(t["health"])
    ax.set_xlim(0, 100)
    for bar, s in zip(bars, scores):
        ax.text(bar.get_width()+1, bar.get_y()+bar.get_height()/2,
                f"{s:.0f}%", va="center", fontsize=9)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

# ─── TAB 3: WEATHER ───
with tabs[2]:
    st.subheader(t["weather_title"])

    zone_names = [z["name_ar"] if L=="ar" else z["name_en"] for z in zones_show]
    sel = st.selectbox("", zone_names)
    sel_zone = zones_show[zone_names.index(sel)]

    forecast = fetch_forecast(sel_zone["lat"], sel_zone["lon"])
    if not forecast.empty:
        fig2, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5), sharex=True)
        ax1.plot(forecast["date"], forecast["max_temp"], "r-o", label="Max", ms=4)
        ax1.plot(forecast["date"], forecast["min_temp"], "b-o", label="Min", ms=4)
        ax1.set_ylabel("°C")
        ax1.legend(fontsize=8)
        ax1.set_title(f"{sel} — {t['weather_title']}")
        ax1.tick_params(axis='x', rotation=30)
        ax2.bar(forecast["date"], forecast["rain"], color="#4895ef", alpha=0.8)
        ax2.set_ylabel("mm")
        ax2.tick_params(axis='x', rotation=30)
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close()

        st.dataframe(forecast.rename(columns={
            "date":"Date","max_temp":"Max °C","min_temp":"Min °C","rain":"Rain mm"
        }), use_container_width=True, hide_index=True)

# ─── TAB 4: FIRES ───
with tabs[3]:
    st.subheader(t["fire_title"])
    fires = fetch_fires()
    if fires.empty:
        st.success(t["no_fires"])
    else:
        st.warning(f"{t['fires_found']}: **{len(fires)}**")
        fire_map = folium.Map(location=[28.0, 3.0], zoom_start=5, tiles="CartoDB dark_matter")
        for _, row in fires.iterrows():
            try:
                folium.CircleMarker(
                    location=[row["latitude"], row["longitude"]],
                    radius=5, color="#ff4500", fill=True,
                    fill_color="#ff4500", fill_opacity=0.8,
                    tooltip=f"🔥 {row.get('acq_date','N/A')}"
                ).add_to(fire_map)
            except: continue
        st_folium(fire_map, width=None, height=450, returned_objects=[])
        st.dataframe(fires[["latitude","longitude","bright_ti4","confidence","acq_date"]].head(20),
                     use_container_width=True, hide_index=True)

# ─── TAB 5: ABOUT ───
with tabs[4]:
    st.markdown(t["about_text"])
    st.info("🔗 GitHub: github.com/djermaneali/algeria-agriwatch")
