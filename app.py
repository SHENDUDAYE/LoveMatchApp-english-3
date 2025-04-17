import streamlit as st
import datetime
from datetime import date
from dateutil import parser

# ------------------------ Basic Data ------------------------

ZODIACS = ["Rat","Ox","Tiger","Rabbit","Dragon","Snake","Horse","Goat","Monkey","Rooster","Dog","Pig"]
TIANGANS = ["Jia","Yi","Bing","Ding","Wu","Ji","Geng","Xin","Ren","Gui"]
DIZHIS  = ["Zi","Chou","Yin","Mao","Chen","Si","Wu","Wei","Shen","You","Xu","Hai"]

# Full 60‑Ganzhi → (Nayin name, element)
NAYIN_MAP = {
    ("JiaZi","YiChou"):("Gold in Sea","Metal"),   ("BingYin","DingMao"):("Fire in Furnace","Fire"),
    # … 省略中间项，请填入完整 60 甲子映射
}

# Zodiac pair relations
LIUHE = [("Rat","Ox"),("Tiger","Pig"),("Rabbit","Dog"),("Dragon","Rooster"),("Snake","Monkey"),("Horse","Goat")]
LIUCHONG = [("Rat","Horse"),("Ox","Goat"),("Tiger","Monkey"),("Rabbit","Rooster"),("Dragon","Dog"),("Snake","Pig")]
LIUHAI = [("Rat","Goat"),("Ox","Horse"),("Tiger","Snake"),("Rabbit","Dragon"),("Dog","Rooster"),("Monkey","Pig")]
SANHE = [
    ("Monkey","Rat","Dragon"),("Tiger","Horse","Dog"),
    ("Snake","Rooster","Ox"),  ("Pig","Rabbit","Goat"),
]

# ------------------------ Core Calculations ------------------------

def get_zodiac(year):
    return ZODIACS[(year - 4) % 12]

def get_ganzhi(year):
    g = TIANGANS[(year - 4) % 10]
    z = DIZHIS[(year - 4) % 12]
    return g+z

def get_nayin(gz):
    for keys, val in NAYIN_MAP.items():
        if gz in keys:
            return val
    return ("Unknown","Unknown")

def zodiac_relations(z1, z2):
    """Return list of relation types:六合,三合,六冲,六害,同属相 or 'Ordinary'"""
    rels = []
    if (z1,z2) in LIUHE or (z2,z1) in LIUHE:
        rels.append("Harmonious Pair (LiuHe)")
    if any(z1 in grp and z2 in grp for grp in SANHE):
        rels.append("Compatible Trio (SanHe)")
    if (z1,z2) in LIUCHONG or (z2,z1) in LIUCHONG:
        rels.append("Clash (LiuChong)")
    if (z1,z2) in LIUHAI or (z2,z1) in LIUHAI:
        rels.append("Conflict (LiuHai)")
    if z1 == z2:
        rels.append("Same Sign")
    return rels or ["Ordinary"]

def wuxing_relation(e1, e2):
    """五行生克"""
    cycle = {"Wood":"Fire","Fire":"Earth","Earth":"Metal","Metal":"Water","Water":"Wood"}
    restr = {v:k for k,v in cycle.items()}
    if cycle.get(e1)==e2:
        return "Generates", f"{e1}→{e2}"
    if cycle.get(e2)==e1:
        return "Generates", f"{e2}→{e1}"
    if restr.get(e1)==e2:
        return "Overcomes", f"{e1}→{e2}"
    if restr.get(e2)==e1:
        return "Overcomes", f"{e2}→{e1}"
    return "Neutral",""

def score_match(z_rels, wx_rel, same_nayin):
    s = 60
    for r in z_rels:
        if "Harmonious" in r: s += 15
        if "Compatible Trio" in r: s += 10
        if "Clash" in r: s -= 10
        if "Conflict" in r: s -= 15
    if wx_rel[0]=="Generates": s += 20
    if wx_rel[0]=="Overcomes": s -= 15
    if same_nayin: s += 10
    return max(min(s,100),0)

def recommend_years(z1, z2):
    """简单择吉婚期：选生肖三合或六合年份"""
    now = date.today().year
    years = []
    for y in range(now, now+6):
        y_z = get_zodiac(y)
        # if year zodiac pairs well with both, pick
        if y_z in {z1,z2}:
            years.append(y)
    return years[:3] or [now,now+1,now+2]

def predict_children(wx_rel):
    if wx_rel[0]=="Generates":
        return "Good fertility prospects; likely healthy offspring."
    if wx_rel[0]=="Overcomes":
        return "May need health care precautions during pregnancy."
    return "Average fertility; nurture and care are key."

# ------------------------ UI ------------------------

st.set_page_config(page_title="Love Match Compatibility Analyzer", layout="wide")
st.title("💖 Love Match Compatibility Analyzer")
st.write("Enter both partners' birth dates to get a full compatibility report.")

col1, col2 = st.columns(2)
with col1:
    b1 = st.date_input("Partner A Birth Date", value=date(1990,1,1), key="A")
with col2:
    b2 = st.date_input("Partner B Birth Date", value=date(1992,1,1), key="B")

if st.button("🔍 Analyze Compatibility"):
    # Basic info
    z1 = get_zodiac(b1.year); gz1 = get_ganzhi(b1.year); ny1, e1 = get_nayin(gz1)
    z2 = get_zodiac(b2.year); gz2 = get_ganzhi(b2.year); ny2, e2 = get_nayin(gz2)
    st.markdown("### 🔎 Basic Info")
    st.write(f"- Partner A: {b1} → {z1}, Pillar: {gz1}, Nayin: {ny1} ({e1})")
    st.write(f"- Partner B: {b2} → {z2}, Pillar: {gz2}, Nayin: {ny2} ({e2})")
    
    # Zodiac
    zr = zodiac_relations(z1,z2)
    st.markdown("### 🐲 Zodiac Relations")
    st.write(", ".join(zr))
    
    # Nayin & Wuxing
    st.markdown("### 🌟 Nayin & Five Elements")
    same_nayin = (e1==e2)
    wxr = wuxing_relation(e1,e2)
    st.write(f"- Elements: {e1} vs {e2}")
    st.write(f"- Relation: {wxr[0]} ({wxr[1]})")
    st.write(f"- Same Nayin Element: {'Yes' if same_nayin else 'No'}")
    
    # Score
    score = score_match(zr, wxr, same_nayin)
    st.markdown("### 🎯 Compatibility Score")
    st.progress(score/100)
    st.write(f"**Score: {score}/100**")
    
    # Plain commentary
    st.markdown("### 💬 Commentary")
    if score>=85:
        st.write("Excellent match! Strong harmony and mutual support.")
    elif score>=70:
        st.write("Good match. Minor differences, but overall compatible.")
    elif score>=50:
        st.write("Average match. Requires understanding and compromise.")
    else:
        st.write("Challenging match. Consider deeper insight and harmony work.")
    
    # Wedding years
    yrs = recommend_years(z1,z2)
    st.markdown("### 📅 Recommended Wedding Years")
    st.write(", ".join(str(y) for y in yrs))
    
    # Children forecast
    st.markdown("### 👶 Children Forecast")
    st.write(predict_children(wxr))
