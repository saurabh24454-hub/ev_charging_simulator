import streamlit as st
import random
import pandas as pd
import matplotlib.pyplot as plt

st.markdown("""
<style>
.stApp { background-color: #f1f8f4; color: #1b5e20; }
header[data-testid="stHeader"] { background: linear-gradient(90deg, #f1f8f4 0%, #2e7d32 50%, #f1f8f4 100%); height: 4px; }
section[data-testid="stSidebar"] { background-color: #e8f5e9 !important; border-right: 1px solid rgba(46,125,50,0.2); }
label, .stMarkdown p { color: #2e7d32 !important; font-weight: 500; }
</style>""", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: #00e676;'>⚡ EV Charging Simulator</h1>", unsafe_allow_html=True)
st.text("Simulates EV charging ports: availability, wait time, queue position, and cost based on your battery level.")

st.sidebar.image("https://tse1.mm.bing.net/th/id/OIP.YMBY9WiqLOLuRavdlOn0XAAAAA?r=0&rs=1&pid=ImgDetMain&o=7&rm=3", width=150)
st.sidebar.title("My Profile")

name = st.sidebar.text_input("Enter your name")
if name:
    st.info(f"Hello {name}! welcome to EV simulator")

phone = st.sidebar.text_input("Enter your phone number 📱")
if phone:
    if phone.isdigit() and len(phone) == 10:
        st.sidebar.success("✅ Valid phone number!")
    else:
        st.sidebar.error("❌ Enter a valid 10-digit number!")

email = st.sidebar.text_input("Enter your email")
if email:
    if "@" in email and "." in email:
        st.sidebar.success(f"Valid email: {email}")
    else:
        st.sidebar.error("Please enter a valid email address.")

car = st.sidebar.radio("🚗 Tell us about your car", ["Hatchback", "Sedan", "SUV", "Bus"], index=None)

CAR_INFO = {
    "Hatchback": {"battery_kwh": 30, "charger_kw": 3.3},
    "Sedan":     {"battery_kwh": 60, "charger_kw": 7.0},
    "SUV":       {"battery_kwh": 80, "charger_kw": 7.0},
    "Bus":       {"battery_kwh": 200, "charger_kw": 50.0},
}
if car:
    st.write(pd.DataFrame({"Vehicle type": list(CAR_INFO), "Battery (kWh)": [v["battery_kwh"] for v in CAR_INFO.values()], "Max charger (kW)": [v["charger_kw"] for v in CAR_INFO.values()]}))

st.sidebar.selectbox("Select your state", ["Andhra Pradesh", "Himachal Pradesh", "Delhi", "Maharashtra", "Karnataka", "Tamil Nadu", "Other"], index=None)

# ---- NEW: Charging mode selector ----
st.sidebar.markdown("---")
charge_mode = st.sidebar.radio("⚡ Charging Mode", ["🐢 Normal", "🚀 Fast"], horizontal=True)
if charge_mode == "🚀 Fast":
    st.sidebar.info("Fast charge uses 50 kW DC — 25% price surcharge. Cars with max < 50 kW won't benefit.")
else:
    st.sidebar.info("Normal charge uses your car's onboard AC charger. Slower but cheaper & gentler on battery.")
# ---- END NEW ----

st.subheader("🚗 Battery Level")
battery = st.slider("Battery Level (%)", 0, 100)
my_bat = battery

# --- simulation state (kept separate from profile so refresh doesn't wipe it) ---
if "charging_ports" not in st.session_state:
    st.session_state.charging_ports = {
        f"Port {i}": {"load": random.randint(1, 8), "kw": random.choice([7.0, 50.0])} for i in range(1, 5)
    }
if "queue" not in st.session_state:
    cars = list(CAR_INFO)
    st.session_state.queue = sorted(
        [{"name": f"EV #{i+1}", "bat": random.randint(5, 80), "car": random.choice(cars)} for i in range(random.randint(2, 5))],
        key=lambda x: x["bat"]
    )
if "booked" not in st.session_state:
    st.session_state.booked = None
if "booking_id" not in st.session_state:
    st.session_state.booking_id = None

charging_ports = st.session_state.charging_ports
queue = st.session_state.queue

c1, c2 = st.columns(2)
if c1.button("🔄 Refresh Station"):
    for k in ["charging_ports", "queue", "booked"]:
        st.session_state.pop(k, None)
    st.rerun()
if c2.button("🔜 Refresh Queue"):
    st.session_state.pop("queue", None)
    st.rerun()


def recommend_port(ports, required_kw):
    eligible = {n: p for n, p in ports.items() if required_kw and p["kw"] >= required_kw}
    if not eligible:
        fastest = max(p["kw"] for p in ports.values())
        eligible = {n: p for n, p in ports.items() if p["kw"] == fastest} if required_kw else ports
    return min(eligible, key=lambda n: eligible[n]["load"])


required_kw = CAR_INFO[car]["charger_kw"] if car else None
# ---- NEW: bump required_kw for fast mode ----
if charge_mode == "🚀 Fast" and car:
    required_kw = max(required_kw, 50.0)
# ---- END NEW ----
best_port = recommend_port(charging_ports, required_kw)

if car:
    eff_kw = min(CAR_INFO[car]["charger_kw"], charging_ports[best_port]["kw"])
    units = (100 - battery) / 100 * CAR_INFO[car]["battery_kwh"]

    # ---- NEW: cost changes based on mode ----
    base_rate = 14.0
    surcharge = 1.25 if charge_mode == "🚀 Fast" else 1.0
    cost = units * base_rate * surcharge
    hours = units / eff_kw if eff_kw else 0

    st.success(f"💰 **{charge_mode} charge** cost to fully charge your {car}: **₹{cost:.2f}**"
               + (" *(includes 25% fast-charge surcharge)*" if charge_mode == "🚀 Fast" else ""))
    st.success(f"⏱️ At **{best_port}** ({charging_ports[best_port]['kw']:.0f} kW), fully charged in **{hours:.2f} hours**")

    # ---- NEW: warn if car can't actually benefit from fast charging ----
    if charge_mode == "🚀 Fast" and CAR_INFO[car]["charger_kw"] < 50.0:
        st.warning(f"⚠️ Your **{car}** supports max {CAR_INFO[car]['charger_kw']} kW — "
                   f"it cannot use full fast-charge speed. You'll pay the surcharge but charge at normal speed!")
    # ---- END NEW ----
else:
    st.warning("⚠️ Please select your car type from the sidebar first!")

st.markdown("---")
st.subheader("📊 Port Population (Live Load)")
names, loads = list(charging_ports), [p["load"] for p in charging_ports.values()]
fig, ax = plt.subplots(figsize=(6, 3))
fig.patch.set_facecolor("#020202"); ax.set_facecolor("#030101")
bars = ax.bar(names, loads, color=["#4F91CE" if v == min(loads) else "#EBFC03" for v in loads], width=0.4)
ax.set_ylabel("No. of EVs", color="#f00707"); ax.set_title("EVs at Each Charging Port", color="#068be4")
ax.tick_params(colors="#068be4")
for bar, val in zip(bars, loads):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1, str(val), ha='center', color='white')
st.pyplot(fig)
st.success(f"✅ Recommended Port → **{best_port}** ({charging_ports[best_port]['kw']:.0f} kW, {charging_ports[best_port]['load']} EVs there)")

st.markdown("---")
st.subheader("📌 Book a Port")
if st.session_state.booked is None:
    if car and st.button(f"📌 Book {best_port} now"):
        charging_ports[best_port]["load"] += 1
        st.session_state.booked = {"port": best_port, "car": car, "battery": battery, "kw": charging_ports[best_port]["kw"]}
        st.session_state.booking_id = f"EV{random.randint(100000, 999999)}"
        st.rerun()
    elif not car:
        st.info("Select your car above to book a port.")
else:
    b = st.session_state.booked
    bid = st.session_state.booking_id
    st.success(f"✅ Booked! **{b['car']}** → **{b['port']}** ({b['kw']:.0f} kW) at {b['battery']}% battery.")
    st.info(f"🎫 Your Booking ID: **#{bid}** — save this for reference!")
    receipt = f"""
====================================
       ⚡ EV CHARGING RECEIPT
====================================
Name        : {name if name else 'N/A'}
Phone       : {phone if phone else 'N/A'}
Booking ID  : #{bid}
Car Type    : {b['car']}
Port        : {b['port']}
Battery     : {b['battery']}%
Mode        : {charge_mode}
Total Cost  : ₹{cost:.2f}
====================================
     Thank you for using EV Simulator!
====================================
"""
    st.download_button("📄 Download Receipt", data=receipt, file_name=f"receipt_{bid}.txt", mime="text/plain")
    if st.button("❌ Cancel booking"):
        charging_ports[b["port"]]["load"] = max(0, charging_ports[b["port"]]["load"] - 1)
        st.session_state.booked = None
        st.session_state.booking_id = None
        st.rerun()

st.markdown("---")
st.title("EV Charging Queue")
position = ["🥇 First", "🥈 Second", "🥉 Third", "#4", "#5", "#6"]
port_names = list(charging_ports)
for i, ev in enumerate(queue):
    icon = "🚨" if ev["bat"] <= 15 else "⚠️" if ev["bat"] <= 30 else "🟢"
    assigned = port_names[i % len(port_names)]
    label = position[i] if i < len(position) else f"#{i + 1}"
    st.write(f"{label} — 🚗 {ev['name']} ({ev['car']}) | 🔋 {ev['bat']}% {icon} | 🔌 → **{assigned}**")
    st.progress(ev["bat"])

my_pos = sum(1 for ev in queue if ev["bat"] <= my_bat) + 1
st.info(f"📍 You are at **{position[my_pos - 1] if my_pos <= len(position) else f'#{my_pos}'}** in the queue!")

st.markdown("---")
st.subheader("💬 Feedback")
rating = st.radio("Rate your experience", ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"], horizontal=True, index=None)
feedback = st.text_area("Any suggestions?", placeholder="Tell us what you think...")
if st.button("Submit Feedback"):
    if rating and feedback:
        st.success("✅ Thanks for your feedback!")
    elif not rating:
        st.warning("⚠️ Please select a rating!")
    else:
        st.warning("⚠️ Please write something before submitting!")