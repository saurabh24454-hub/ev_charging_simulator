import streamlit as st
import random
import pandas as pd
import matplotlib.pyplot as plt


# 1. Page Configuration
st.set_page_config(page_title="EV Charging Simulator", layout="wide")

# 2. Advanced EV Cyber-Grid Background & Custom UI Styling
st.markdown(
    """
    <style>
    /* 1. Technical Cyber-Grid Background */
    .stApp {
        background-color: #0b0f17;
        background-image: 
            linear-gradient(rgba(0, 230, 118, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 230, 118, 0.03) 1px, transparent 1px);
        background-size: 30px 30px;
        color: #e2e8f0;
    }
    
    /* 2. Top Header Glow Bar */
    header[data-testid="stHeader"] {
        background: linear-gradient(90deg, #0b0f17 0%, #00e676 50%, #0b0f17 100%);
        height: 4px;
    }
    
    /* 3. Glassmorphic Sidebar (Semi-transparent Blur) */
    section[data-testid="stSidebar"] {
        background-color: rgba(16, 22, 34, 0.85) !important;
        backdrop-filter: blur(12px);
        border-right: 1px solid rgba(0, 230, 118, 0.15);
        box-shadow: 5px 0 25px rgba(0, 0, 0, 0.5);
    }
    
    /* 4. Sleek Futuristic Cards for Simulator Displays */
    .ev-container {
        background: rgba(22, 30, 46, 0.7);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(0, 230, 118, 0.15);
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: all 0.3s ease-in-out;
        margin-bottom: 25px;
    }
    
    /* Subtle hover glow effect for interactive feel */
    .ev-container:hover {
        border-color: rgba(0, 230, 118, 0.4);
        box-shadow: 0 0 20px rgba(0, 230, 118, 0.1);
    }
    
    /* Neon Text Accents */
    .neon-text {
        color: #00e676;
        text-shadow: 0 0 10px rgba(0, 230, 118, 0.3);
        font-family: 'Courier New', monospace;
        font-weight: bold;
    }
    
    /* Standardizing Input Labels to match dark theme */
    label, .stMarkdown p {
        color: #94a3b8 !important;
        font-weight: 500;
    }
    </style>
    """,
    unsafe_allow_html=True

)

st.text("So this is a simple simulator for EV charging stations, it tells you about the available ports for your EV and tells how much time you have to wait for the port to be free. It also tells you about the waiting queue and your position in it based on your battery level.")
st.sidebar.title("My Profile")
st.sidebar.text("please provide your details below:")

name = st.sidebar.text_input("Enter your name")
if name:
    st.sidebar.info(f"Hello {name}! Let's get started.")
email = st.sidebar.text_input("Enter your email")
if email:
    if "@" in email and "." in email:
        st.success(f"Valid email: {email}")
    else:
        st.error("Please enter a valid email address.")
car=st.sidebar.radio("🚗 Tell us about your car", ["Hatchback", "Sedan", "SUV", "Electric Bus"], index=None)

f=pd.DataFrame({"Vehicle type":["sedan","hatchback","suv","bus"],"Battery capacity (kWh)":["60","30","80","200"],"Max charger (kW)":["7.0","3.3","7.0","50.0"]})
if car:
    st.write(f)
st.sidebar.selectbox("Selecy your state",["Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar",
    "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh",
    "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra",
    "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
    "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal","Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli","Daman and Diu", "Delhi", "Jammu and Kashmir", "Ladakh","Lakshadweep", "Puducherry"],index=None)

CAR_INFO = {
    "Hatchback": {"battery_kwh": 30,  "charger_kw": 3.3},
    "Sedan":     {"battery_kwh": 60,  "charger_kw": 7.0},
    "SUV":       {"battery_kwh": 80,  "charger_kw": 7.0},
    "Bus":       {"battery_kwh": 200, "charger_kw": 50.0},
}

BATTERY = {"<10%": 5, "10–25%": 17, "25–50%": 37, "50–75%": 62, ">75%": 80}

WAITING = {"Now": 0, "5 min": 5, "10 min": 10, "20 min": 20, "30+ min": 60}

def make_ports():
    ports = []
    for i in range(1, 7):
        wait = random.choice([0, 5, 10, 20, 30, 60])
        ports.append({
            "id": i,
            "wait": wait,
            "charger": random.choice(["Fast (50 kW)", "Standard (10 kW)"]),
            "status": "🟢 Free" if wait == 0 else f"{'🟡' if wait <= 10 else '🔴'} Free in {wait} min"
        })
    return ports

st.subheader("🚗 Tell us about your car")
battery = battery = st.slider(
    "Battery Level (%)",
    min_value=0,
    max_value=100,
    value=50
)

my_bat = battery
wait    =st.selectbox("how much time you are here ?",["0 mins", "5 mins", "10 mins", "20 mins", "30+ mins"])
w = {"0 mins":0, "5 mins":5, "10 mins":10, "20 mins":20, "30+ mins":60}[wait]

if st.button("🔄 Refresh Station"): st.session_state.clear()
 
if "ports" not in st.session_state:
    st.session_state.ports = [{"id":i, "wait":random.choice([0,0,5,10,30]), "kw":random.choice([7,50])} for i in range(1,7)]
    queue = [{"name":f"EV #{i+1}", "bat":random.randint(5,80)} for i in range(random.randint(0,4))]
    st.session_state.queue = sorted(queue, key=lambda x: x["bat"])

# ── NEW: 3 Charging Ports ──────────────────────────────────────────────────────
if "charging_ports" not in st.session_state:
    st.session_state.charging_ports = {
        "Port 1": random.randint(1, 8),
        "Port 2": random.randint(1, 8),
        "Port 3": random.randint(1, 8),
    }

ports = st.session_state.ports
queue = st.session_state.queue
charging_ports = st.session_state.charging_ports

# ──  Bar Graph – Population at Each Port ───────────────────────────────────
st.markdown("---")
st.subheader("📊 Port Population (Live Load)")

port_names = list(charging_ports.keys())
port_loads = list(charging_ports.values())
colors = ["#05fce7" if v == min(port_loads) else "#471675" for v in port_loads]

fig, ax = plt.subplots(figsize=(6, 3))
fig.patch.set_facecolor("#020202")
ax.set_facecolor("#030101")
bars = ax.bar(port_names, port_loads, color=colors, width=0.4, edgecolor="#000000", linewidth=0.8)
ax.set_ylabel("No. of EVs", color="#f00707")
ax.set_title("EVs at Each Charging Port", color="#068be4", fontsize=13)
ax.tick_params(colors="#068be4")
for spine in ax.spines.values():
    spine.set_edgecolor("#0a0b0c")
for bar, val in zip(bars, port_loads):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, str(val),
            ha='center', color='white', fontsize=11)
st.pyplot(fig)

best_port = min(charging_ports, key=charging_ports.get)
st.success(f"✅ Recommended Port for you → **{best_port}** (Only {charging_ports[best_port]} EVs present — least crowded!)")

st.markdown("---")
st.title("EV Charging Queue")
if st.button("Refresh Queue"):
    st.session_state.clear()
if "queue" not in st.session_state:
     cars  = ["Hatchback", "Sedan", "SUV", "Electric Bus"]
     queue = [{"name": f"EV #{i+1}", "bat": random.randint(5, 70), "car": random.choice(cars)} for i in range(random.randint(2, 5))]
     st.session_state.queue = sorted(queue, key=lambda x: x["bat"])

st.markdown("---")

position = ["🥇 First", "🥈 Second", "🥉 Third", "#4 Fourth", "#5 Fifth"]

for i, ev in enumerate(st.session_state.queue):
    icon = "🚨" if ev["bat"] <= 15 else ("⚠️" if ev["bat"] <= 30 else "🟢")

    assigned = list(charging_ports.keys())[i % 3]
    st.write(f"{position[i]}  —  🚗 {ev['name']} |  🔋 {ev['bat']}%  {icon}  |  🔌 Go to → **{assigned}**")
    st.progress(ev["bat"])
st.markdown("---")
if battery is None:
    st.markdown("---")

my_bat = battery

count = sum(
    1 for ev in st.session_state.queue
    if ev["bat"] <= my_bat
)

my_pos = count + 1

pos_name = position[my_pos - 1] if my_pos <= len(position) else f"#{my_pos}"

st.info(f"📍 Currently you are at **{pos_name}** position in the queue!")

st.success(f"🔌 Head to **{best_port}** — it's the least crowded port for you right now!")