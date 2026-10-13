import json
import html
import re
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from backend.ai import ask_ai
from backend.nlp import extract_symptoms
from backend.predict import predict
from backend.report import create_report
from backend.simulator import stream_vitals

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DOCTORS_FILE = DATA_DIR / "doctors.csv"
LEGACY_DOCTORS_FILE = DATA_DIR / "doctors.csv.csv"
REQUESTS_FILE = DATA_DIR / "consultation_requests.csv"


def hero(eyebrow, title, subtitle, variant=""):
    hero_class = "hg-hero hg-hero-fitness" if variant == "fitness" else "hg-hero"
    st.markdown(
        f"<div class='{hero_class}'><div class='hg-eyebrow'>{eyebrow}</div>"
        f"<h1>{title}</h1><p>{subtitle}</p></div>",
        unsafe_allow_html=True,
    )


def _navigate_to(page):
    st.session_state["workspace_page"] = page


def dashboard_page():
    hero("CAREBUDDY HEALTH DASHBOARD", "Your health, in one calm space.", "A clear view of your latest check-in, helpful next steps and everyday wellness tools.")
    result = st.session_state.get("last_symptom_result")
    signal, signal_color, _ = _attention_signal(result) if result else ("Not assessed", "yellow", "")
    metrics = st.columns(4)
    signal_emoji = {"red": "🔴", "yellow": "🟡", "green": "🟢"}[signal_color]
    metrics[0].metric("Attention signal", f"{signal_emoji} {signal}" if result else "Not assessed")
    metrics[1].metric("Symptoms noted", len(result["symptoms"]) if result else "—")
    metrics[2].metric("Heart rate entered", f"{result['hr']} bpm" if result else "—")
    metrics[3].metric("SpO₂ entered", f"{result['spo2']}%" if result else "—")

    st.markdown("### Choose your next step")
    quick_actions = st.columns(3)
    actions = [
        ("🩺", "Symptom checker", "Describe symptoms and organize the details for a health conversation.", "AI Symptom Analyzer"),
        ("✨", "Fitness & nutrition", "Build a flexible movement plan and find balanced meal inspiration.", "Fitness AI Coach"),
        ("👩‍⚕️", "Doctor connections", "Browse the directory and save a demo consultation request.", "Doctor Consultation"),
    ]
    for col, (icon, title, description, destination) in zip(quick_actions, actions):
        with col:
            st.markdown(f"<div class='hg-card'><span class='hg-pill'>{icon} CAREBUDDY</span><h3>{title}</h3><p>{description}</p></div>", unsafe_allow_html=True)
            st.button(f"Open {title}", key=f"dashboard_{destination}", use_container_width=True,
                      on_click=_navigate_to, args=(destination,))

    st.markdown("### Your latest check-in")
    if not result:
        st.markdown("<div class='hg-soft-panel'><h3>Start with a quick check-in</h3><p>Your dashboard will show the information you choose to enter. Nothing here is connected to a wearable or a medical record.</p></div>", unsafe_allow_html=True)
    else:
        left, right = st.columns([1.15, 1])
        with left:
            st.markdown("<div class='hg-card'><span class='hg-pill'>CHECK-IN SUMMARY</span><h3>What you reported</h3></div>", unsafe_allow_html=True)
            if result["symptoms"]:
                labels = [html.escape(s.replace("_", " ").title()) for s in result["symptoms"]]
                chips = " ".join(f"<span class='hg-pill'>{label}</span>" for label in labels)
                st.markdown(chips, unsafe_allow_html=True)
            else:
                st.write("No supported symptom keywords were selected or detected.")
            st.write("**Duration:**", f"{result['duration_days']} day(s)" if result["duration_days"] else "Not provided")
            st.write("**Age entered:**", result["age"])
            st.write("**Additional notes:**", result["text"] or "None")
        with right:
            level, color, message = _attention_signal(result)
            st.markdown(f"<div class='hg-card'><span class='hg-pill'>SAFETY CHECK</span><h3>What to consider next</h3><div class='hg-risk-signal hg-risk-{color}'><span class='hg-signal-dot'></span><div><small>RULE-BASED RISK INDICATOR</small><strong>{level} LEVEL</strong></div></div><p class='hg-risk-copy'>{html.escape(message)}</p></div>", unsafe_allow_html=True)
            st.caption("Entered readings are saved only in this app session and are not verified by a device.")

        estimates = st.session_state.get("last_pattern_estimates", [])
        st.markdown("### Possible patterns · demo model")
        st.caption("The classifier was trained on synthetic records. Scores show broad pattern matching for demonstration only; they are not probabilities of a disease, causes, diagnoses, or clinical advice. Several uncollected model inputs use fixed demo defaults.")
        if estimates:
            pattern_data = pd.DataFrame([
                {"Pattern": label, "Model estimate (%)": round(probability * 100, 1)}
                for label, probability in estimates
            ]).sort_values("Model estimate (%)", ascending=False)
            chart_left, chart_right = st.columns(2)
            with chart_left:
                bar = px.bar(
                    pattern_data, x="Model estimate (%)", y="Pattern", orientation="h",
                    color="Pattern", text="Model estimate (%)", template="plotly_white",
                    color_discrete_sequence=["#7555e8", "#f26b70", "#17b890", "#49a7ec", "#ffc36b", "#a66be0", "#55bca8", "#f39b64"],
                    title="Demo pattern scores",
                )
                bar.update_traces(texttemplate="%{text:.1f}%", textposition="outside", cliponaxis=False)
                bar.update_layout(showlegend=False, height=390, margin=dict(l=10, r=35, t=55, b=20), xaxis_range=[0, 100], yaxis_title="")
                st.plotly_chart(bar, use_container_width=True)
            with chart_right:
                donut = px.pie(
                    pattern_data, names="Pattern", values="Model estimate (%)", hole=.58,
                    color="Pattern", template="plotly_white",
                    color_discrete_sequence=["#7555e8", "#f26b70", "#17b890", "#49a7ec", "#ffc36b", "#a66be0", "#55bca8", "#f39b64"],
                    title="Pattern score distribution · demo only",
                )
                donut.update_traces(textinfo="percent", textposition="inside")
                donut.update_layout(height=390, margin=dict(l=10, r=10, t=55, b=15), legend=dict(font=dict(size=10)))
                st.plotly_chart(donut, use_container_width=True)
        elif st.session_state.get("pattern_estimate_error"):
            st.info(st.session_state["pattern_estimate_error"])
        else:
            st.info("Complete a symptom check-in to see the prototype's demo pattern charts here.")

    ai_guidance = st.session_state.get("last_ai_guidance")
    if ai_guidance:
        st.markdown("### Health information from your last check-in")
        st.markdown(f"<div class='hg-soft-panel'>{html.escape(ai_guidance).replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)


def _urgent_flags(symptoms, temp, spo2, sbp):
    flags = []
    if "chest_pain" in symptoms:
        flags.append("Chest pain")
    if "breathlessness" in symptoms:
        flags.append("Breathing difficulty")
    if spo2 <= 90:
        flags.append("Very low entered oxygen saturation (SpO₂ ≤ 90%)")
    if sbp >= 180:
        flags.append("Very high entered systolic blood pressure (≥ 180 mmHg)")
    if temp >= 40:
        flags.append("Very high entered temperature (≥ 40°C)")
    return flags


def _attention_signal(result):
    """A transparent, unvalidated UI cue based only on the prototype's entered values."""
    symptoms = result.get("symptoms", [])
    urgent = (
        bool(result.get("flags"))
        or "chest_pain" in symptoms
        or "breathlessness" in symptoms
        or result.get("temp", 0) >= 40
        or result.get("spo2", 100) <= 92
        or result.get("sbp", 0) >= 180
    )
    if urgent:
        return "High", "red", "A warning sign or concerning value was entered. Seek prompt medical advice; for severe or sudden symptoms, contact local emergency services."
    moderate = (
        len(symptoms) >= 2
        or (result.get("duration_days") or 0) > 3
        or result.get("temp", 0) >= 38
        or result.get("spo2", 100) <= 94
        or result.get("sbp", 0) >= 140
    )
    if moderate:
        return "Medium", "yellow", "Several symptoms or an entered value may deserve a closer look. Consider contacting a qualified healthcare professional, especially if symptoms persist or worsen."
    return "Low", "green", "No attention trigger was detected by this simple prototype. A low signal does not rule out illness or an emergency."


def _model_input(result):
    """Build the complete feature row expected by the educational synthetic classifier."""
    symptoms = set(result.get("symptoms", []))
    height_cm = 167.0
    bmi = 24.8
    row = {
        "age": result.get("age", 25), "gender": "Other", "height_cm": height_cm,
        "weight_kg": round(bmi * (height_cm / 100) ** 2, 1), "bmi": bmi,
        "smoking": "Never", "activity_level": "Moderate", "sleep_hours": 7.0,
        "stress_score": 5.0, "temperature_c": result.get("temp", 36.8),
        "heart_rate_bpm": result.get("hr", 75), "systolic_bp": result.get("sbp", 120),
        "diastolic_bp": result.get("dbp", 80), "spo2_pct": result.get("spo2", 98),
        "glucose_mg_dl": 96,
    }
    for symptom in ("fever", "cough", "headache", "fatigue", "sore_throat", "nausea", "vomiting", "diarrhea", "rash", "joint_pain", "chest_pain", "breathlessness", "dizziness"):
        row[symptom] = int(symptom in symptoms)
    row["symptom_count"] = sum(row[symptom] for symptom in ("fever", "cough", "headache", "fatigue", "sore_throat", "nausea", "vomiting", "diarrhea", "rash", "joint_pain", "chest_pain", "breathlessness", "dizziness"))
    return row


def symptom_page():
    hero("CARE STARTS WITH LISTENING", "AI Symptom Checker", "Select what you’re experiencing, add any details, and organize a clear check-in for your care conversation.")
    st.info("This educational prototype cannot diagnose or recommend medicine. For severe or rapidly worsening symptoms, seek urgent medical care.")

    symptom_options = [
        ("Fever", "General", "fever"), ("Cough", "Respiratory", "cough"),
        ("Chest pain", "Cardiac", "chest_pain"), ("Nausea", "Digestive", "nausea"),
        ("Headache", "Neurological", "headache"), ("Fatigue", "General", "fatigue"),
        ("Stomach pain", "Digestive", "stomach_pain"), ("Shortness of breath", "Respiratory", "breathlessness"),
        ("Dizziness", "Neurological", "dizziness"), ("Muscle / joint pain", "Musculoskeletal", "joint_pain"),
        ("Sore throat", "Respiratory", "sore_throat"), ("Skin rash", "Skin", "rash"),
    ]
    with st.form("symptom_analyzer_form"):
        st.markdown("<div class='hg-section-label'>Select your symptoms</div>", unsafe_allow_html=True)
        st.caption("Choose all that apply. You can also describe anything else in your own words below.")
        selected_symptoms = []
        for start in range(0, len(symptom_options), 3):
            cols = st.columns(3)
            for col, (label, category, key) in zip(cols, symptom_options[start:start + 3]):
                with col:
                    with st.container(border=True):
                        if st.checkbox(label, key=f"symptom_select_{key}"):
                            selected_symptoms.append(key)
                        st.caption(category)
        symptom_text = st.text_area("Additional notes (optional)", placeholder="When did it start? What else would you like your care team to know?", height=90)
        c1, c2, c3, c4 = st.columns(4)
        age = c1.number_input("Age", min_value=0, max_value=120, value=25)
        temp = c2.number_input("Temperature (°C), if known", min_value=30.0, max_value=45.0, value=36.8, step=0.1)
        hr = c3.number_input("Heart rate, if known", min_value=0, max_value=250, value=75)
        spo2 = c4.number_input("SpO₂ %, if known", min_value=0, max_value=100, value=98)
        c5, c6 = st.columns(2)
        sbp = c5.number_input("Systolic blood pressure, if known", min_value=0, max_value=300, value=120)
        dbp = c6.number_input("Diastolic blood pressure, if known", min_value=0, max_value=200, value=80)
        consent = st.checkbox("I understand this is educational information and not a medical diagnosis.")
        submitted = st.form_submit_button("Analyze symptoms", use_container_width=True)

    if submitted:
        if not symptom_text.strip() and not selected_symptoms:
            st.error("Select at least one symptom or add a note before analyzing.")
            return
        if not consent:
            st.error("Please acknowledge the safety note before continuing.")
            return
        parsed = extract_symptoms(symptom_text)
        symptoms = sorted(set(parsed.get("symptoms", []) + selected_symptoms))
        flags = _urgent_flags(symptoms, temp, spo2, sbp)
        entered_text = symptom_text.strip()
        if selected_symptoms:
            selected_labels = [label for label, _, key in symptom_options if key in selected_symptoms]
            selected_summary = "Selected symptoms: " + ", ".join(selected_labels)
            entered_text = f"{selected_summary}. {entered_text}" if entered_text else selected_summary
        
        # Reset previous AI session state on a new symptom submission
        latest_result = {
            "text": entered_text, "symptoms": symptoms, "duration_days": parsed.get("duration_days"),
            "age": age, "temp": temp, "hr": hr, "spo2": spo2, "sbp": sbp, "dbp": dbp, "flags": flags,
        }
        st.session_state["last_symptom_result"] = latest_result
        try:
            with st.spinner("Preparing the educational pattern estimate..."):
                _, estimates = predict(_model_input(latest_result), top_k=None)
            st.session_state["last_pattern_estimates"] = estimates
            st.session_state.pop("pattern_estimate_error", None)
        except Exception:
            st.session_state["last_pattern_estimates"] = []
            st.session_state["pattern_estimate_error"] = "The demo model could not create a pattern estimate. Your check-in was still saved."
        if "chat_history" in st.session_state:
            del st.session_state["chat_history"]
        if "last_ai_guidance" in st.session_state:
            del st.session_state["last_ai_guidance"]
            
        st.success("Analysis complete! Click below or check the **Overview** page to see your charts and recommendations.")

    result = st.session_state.get("last_symptom_result")
    if result:
        st.markdown("## Your check-in summary")
        left, right = st.columns([1, 1])
        with left:
            st.markdown("<div class='hg-card'><span class='hg-pill'>INPUT SUMMARY</span><h3>Symptoms detected</h3></div>", unsafe_allow_html=True)
            if result["symptoms"]:
                st.write(" · ".join(s.replace("_", " ").title() for s in result["symptoms"]))
            else:
                st.write("No supported symptom keywords were detected.")
            st.write("**Reported duration:**", f"{result['duration_days']} day(s)" if result["duration_days"] else "Not detected")
            st.write("**Age entered:**", result["age"])
            
        with right:
            level, color, message = _attention_signal(result)
            st.markdown(f"<div class='hg-card'><span class='hg-pill'>SAFETY CHECK</span><h3>What to consider next</h3><div class='hg-risk-signal hg-risk-{color}'><span class='hg-signal-dot'></span><div><small>RULE-BASED RISK INDICATOR</small><strong>{level} LEVEL</strong></div></div><p class='hg-risk-copy'>{html.escape(message)}</p></div>", unsafe_allow_html=True)
            st.caption("This rule-based signal is not a validated medical risk score or diagnosis.")

        if st.button("Generate AI health-information guidance", type="primary"):
            context = (
                f"Age: {result['age']}; reported symptoms: {result['text']}; detected symptom keywords: {result['symptoms']}; "
                f"duration in days: {result['duration_days']}; temperature C: {result['temp']}; heart rate: {result['hr']}; "
                f"SpO2: {result['spo2']}; systolic BP: {result['sbp']}; diastolic BP: {result['dbp']}; warning triggers: {result['flags']}."
            )
            prompt = ("Provide general health information with an empathetic, warm, and human-like tone. Structure the response clearly with a Risk Assessment (Low, Mid, or High Risk), Probabilistic Insights, Friendly Self-Care Suggestions, and Advice on When to Consult a Doctor. Do not diagnose or prescribe.")
            
            with st.spinner("Preparing cautious health-information guidance..."):
                answer = ask_ai(prompt, context)
            
            st.session_state["last_ai_guidance"] = answer
            st.session_state["chat_history"] = [{"role": "assistant", "content": answer}]

        # Render AI Guidance & Interactive Chat Box if guidance exists
        if "last_ai_guidance" in st.session_state:
            st.markdown("### AI guidance")
            st.markdown(st.session_state["last_ai_guidance"])
            st.caption("AI-generated information may be incomplete or wrong. Verify medical decisions with a qualified healthcare professional.")
            
            st.markdown("---")
            st.markdown("### 💬 Help Me Understand Better (Interactive Follow-Ups)")
            st.markdown("<p style='color: #8d99ae;'>Type your answers to the follow-up questions below, and HealthBuddy AI will guide you further!</p>", unsafe_allow_html=True)

            if "chat_history" not in st.session_state:
                st.session_state["chat_history"] = []

            # Display conversation history
            for message in st.session_state["chat_history"]:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # Interactive chat input box for user answers
            user_reply = st.chat_input("Type your answers here (e.g., 'I've had this for 2 days and tried paracetamol')...")
            
            if user_reply:
                st.session_state["chat_history"].append({"role": "user", "content": user_reply})
                with st.chat_message("user"):
                    st.markdown(user_reply)

                with st.spinner("HealthBuddy AI is thinking..."):
                    follow_up_prompt = f"The user answered the follow-up questions with: '{user_reply}'. Provide further warm, empathetic guidance, friendly recommendations, and answer their input directly."
                    ai_reply = ask_ai(follow_up_prompt, context=user_reply)
                    
                    st.session_state["chat_history"].append({"role": "assistant", "content": ai_reply})
                    with st.chat_message("assistant"):
                        st.markdown(ai_reply)
def _doctor_template():
    return pd.DataFrame(columns=[
        "doctor_name", "specialty", "qualification", "experience_years", "clinic_or_hospital",
        "phone", "email", "consultation_mode", "availability", "booking_url", "verified"
    ])


def _load_doctors():
    path = DOCTORS_FILE if DOCTORS_FILE.exists() else LEGACY_DOCTORS_FILE
    if not path.exists():
        return _doctor_template()
    try:
        return pd.read_csv(path).fillna("")
    except Exception:
        return _doctor_template()


def doctors_page():
    hero("CARE CONNECTIONS", "Doctor consultation", "Browse the doctor directory and submit a demo request for an appointment.")
    st.caption("Directory details come from the CSV and are not independently verified by this app.")
    doctors = _load_doctors()

    if doctors.empty:
        st.markdown("<div class='hg-card'><span class='hg-pill'>DIRECTORY SETUP</span><h3>Your doctor directory is ready to populate</h3><p>Add doctors to <b>data/doctors.csv</b>.</p></div>", unsafe_allow_html=True)
    else:
        for start in range(0, len(doctors), 3):
            cols = st.columns(3)
            for col, (_, doc) in zip(cols, doctors.iloc[start:start+3].iterrows()):
                name = str(doc.get("doctor_name", "Doctor profile")) or "Doctor profile"
                specialty = str(doc.get("specialty", "Specialty not added")) or "Specialty not added"
                hospital = str(doc.get("clinic_or_hospital", "Clinic details")) or "Clinic details"
                with col:
                    st.markdown(
                        f"<div class='hg-card'><span class='hg-pill'>{html.escape(specialty)}</span>"
                        f"<h3>👨‍⚕️ {html.escape(name)}</h3>"
                        f"<p>{html.escape(hospital)}</p></div>",
                        unsafe_allow_html=True,
                    )
                    phone = str(doc.get("phone", "")).strip()
                    if phone: st.write(f"☎️ {phone}")
                    url = str(doc.get("booking_url", "")).strip()
                    if url.startswith("https://") or url.startswith("http://"):
                        st.link_button("Open booking page", url)

    st.markdown("## Request a consultation")
    with st.form("consultation_request_form"):
        c1, c2 = st.columns(2)
        patient_name = c1.text_input("Your name")
        contact = c2.text_input("Phone or email for follow-up")
        specialty_options = ["General Medicine", "Cardiology", "Dermatology", "Paediatrics", "Mental Health", "Orthopaedics", "Other"]
        specialty = st.selectbox("Preferred specialty", specialty_options)
        mode = st.selectbox("Preferred consultation", ["Online", "In person", "Either"])
        preferred_date = st.date_input("Preferred date", min_value=date.today())
        summary = st.text_area("Brief reason for consultation", max_chars=1000)
        request_consent = st.checkbox("I understand this is a demo request and no appointment is confirmed.")
        send = st.form_submit_button("Save consultation request", use_container_width=True)
    if send:
        if not patient_name.strip() or not contact.strip():
            st.error("Enter your name and a contact method to save the request.")
        elif not request_consent:
            st.error("Please acknowledge that this is a demo request.")
        else:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            record = pd.DataFrame([{
                "request_id": datetime.now().strftime("REQ-%Y%m%d-%H%M%S"),
                "created_at": datetime.now().isoformat(timespec="seconds"),
                "patient_name": patient_name.strip(), "contact": contact.strip(),
                "preferred_specialty": specialty, "consultation_mode": mode,
                "preferred_date": preferred_date.isoformat(), "reason_summary": summary.strip(),
                "status": "Pending manual follow-up"
            }])
            record.to_csv(REQUESTS_FILE, mode="a", header=not REQUESTS_FILE.exists(), index=False)
            st.success("Demo request saved locally. Your appointment request has been recorded.")


def ai_page():
    hero("HEALTH INFORMATION", "AI Health Assistant", "Ask general health questions and get careful, educational explanations.")
    with st.form("ai_assistant_form"):
        q = st.text_area("What would you like to understand?", placeholder="Ask a question...", height=110)
        submitted = st.form_submit_button("Ask CareBuddy AI", use_container_width=True)
    if submitted:
        if not q.strip():
            st.error("Please enter a question.")
        else:
            with st.spinner("Generating educational information..."):
                st.write(ask_ai(q))


def _fitness_plan(profile):
    """Create a practical starter plan from a small set of user-selected preferences."""
    goal = profile["goal"]
    level = profile["level"]
    days = profile["days"]
    setting = profile["setting"]
    duration = profile["duration"]
    equipment = "gym" if setting == "Gym" else "bodyweight/home"

    if level == "New to training":
        moves = {
            "Full body A": ["Squat to chair · 3 × 8–10", "Incline push-up · 3 × 6–10", "Glute bridge · 3 × 10–12", "Dead bug · 2 × 8 each side"],
            "Full body B": ["Hip hinge practice · 3 × 8", "Supported row · 3 × 8–12", "Step-up · 2 × 8 each side", "Bird dog · 2 × 8 each side"],
        }
        moves["Strength A"] = moves["Full body A"]
        moves["Strength B"] = moves["Full body B"]
    else:
        moves = {
            "Strength A": ["Squat variation · 3 × 8–12", "Push-up or chest press · 3 × 8–12", "Hip hinge · 3 × 8–12", "Plank · 3 × 20–40 sec"],
            "Strength B": ["Split squat · 3 × 8 each side", "Row variation · 3 × 8–12", "Glute bridge or hip thrust · 3 × 10–15", "Dead bug · 3 × 8 each side"],
        }
        moves["Full body A"] = moves["Strength A"]
        moves["Full body B"] = moves["Strength B"]
    if setting == "Gym":
        moves["Full body A"] = ["Goblet or machine squat · 3 × 8–12", "Chest press · 3 × 8–12", "Cable row · 3 × 8–12", "Hip hinge · 3 × 8–10"]
        moves["Full body B"] = ["Leg press · 3 × 8–12", "Lat pulldown · 3 × 8–12", "Dumbbell shoulder press · 2 × 8–10", "Farmer carry · 3 × 30 sec"]
        moves["Strength A"] = moves["Full body A"]
        moves["Strength B"] = moves["Full body B"]

    schedule = []
    if days == 2:
        schedule = [("Day 1", "Full body A"), ("Day 2", "Full body B")]
    elif days == 3:
        schedule = [("Day 1", "Full body A"), ("Day 2", "Easy cardio + mobility"), ("Day 3", "Full body B")]
    elif days == 4:
        schedule = [("Day 1", "Strength A"), ("Day 2", "Easy cardio + mobility"), ("Day 3", "Strength B"), ("Day 4", "Easy cardio + mobility")]
    else:
        schedule = [("Day 1", "Strength A"), ("Day 2", "Easy cardio"), ("Day 3", "Strength B"), ("Day 4", "Mobility + walk"), ("Day 5", "Full body A")]

    if goal == "Build strength & muscle":
        focus = "Use a comfortable load that leaves about 2–3 good reps in reserve. Add a rep before adding weight."
    elif goal == "Improve fitness & energy":
        focus = "Keep most cardio at a pace where you can still talk. Build weekly time gradually."
    elif goal == "Lose body fat & build lean muscle":
        focus = "Pair regular strength training with balanced, satisfying meals. Aim for gradual, sustainable changes rather than restrictive dieting."
    else:
        focus = "Pair regular movement with filling, balanced meals. Avoid crash diets; steady habits are easier to sustain."

    meal_sets = {
        "Everything": ["Oats, yogurt and fruit", "Rice or potatoes + chicken/tofu + vegetables", "Eggs or beans on toast + salad", "Fruit with yogurt or nuts"],
        "Vegetarian": ["Oats, yogurt and fruit", "Rice + lentils/paneer/tofu + vegetables", "Eggs or chickpeas on toast + salad", "Fruit with yogurt or nuts"],
        "Vegan": ["Oats with soy milk, seeds and fruit", "Rice + lentils/tofu + vegetables", "Chickpea bowl with whole grains and salad", "Fruit with hummus or nuts"],
    }
    return {"schedule": schedule, "moves": moves, "focus": focus, "meals": meal_sets[profile["food"]], "equipment": equipment, "duration": duration}


def fitness_page():
    st.markdown("<div class='hg-fitness-page'></div>", unsafe_allow_html=True)
    hero("FITNESS · FOOD · RECOVERY", "Own your strength.", "A training dashboard built around your routine—show up, log a small win, and keep your momentum going.", variant="fitness")
    st.caption("Wellness guidance only. It isn't medical care or a substitute for a qualified trainer or dietitian. Stop if exercise causes pain, chest discomfort, faintness or unusual shortness of breath.")

    settings_section = st.expander("Adjust training preferences", expanded=False) if st.session_state.get("fitness_profile") else st.container()
    with settings_section:
        with st.form("fitness_profile_form"):
            st.markdown("### Set up your training dashboard")
            c1, c2 = st.columns(2)
            goal = c1.selectbox("Your main goal", ["Improve fitness & energy", "Build strength & muscle", "Lose body fat & build lean muscle", "Build a sustainable routine"])
            level = c2.selectbox("Training experience", ["New to training", "Some experience", "Regular training"])
            c3, c4, c5 = st.columns(3)
            setting = c3.selectbox("Where do you train?", ["At home", "Gym"])
            days = c4.select_slider("Days available each week", options=[2, 3, 4, 5], value=3)
            duration = c5.selectbox("Time per session", [20, 30, 45, 60], index=1, format_func=lambda value: f"{value} minutes")
            food = st.selectbox("Food preference", ["Everything", "Vegetarian", "Vegan"])
            focus_note = st.text_input("Anything you want your coach to keep in mind? (optional)", placeholder="For example: low-impact options, busy mornings")
            ready = st.checkbox("I feel well enough to start gentle exercise and will adapt or stop if something feels wrong.")
            generated = st.form_submit_button("Build my fitness dashboard", type="primary", use_container_width=True)

    if generated:
        if not ready:
            st.error("Please confirm you feel well enough to begin. If you have a health condition, injury, or are unsure, check with a qualified professional first.")
        else:
            st.session_state["fitness_profile"] = {"goal": goal, "level": level, "setting": setting, "days": days, "duration": duration, "food": food, "note": focus_note.strip()}
            st.session_state["fitness_plan"] = _fitness_plan(st.session_state["fitness_profile"])

    profile = st.session_state.get("fitness_profile")
    plan = st.session_state.get("fitness_plan")
    if not profile or not plan:
        st.markdown("<div class='hg-fitness-panel hg-fitness-onboarding'><span class='hg-fitness-kicker'>START WHERE YOU ARE</span><h2>Your next rep starts here.</h2><p>Choose your training style above to unlock your weekly split, simple meal ideas and a personal progress board.</p><div class='hg-fitness-orbit'>✦</div></div>", unsafe_allow_html=True)
        return

    today_key = date.today().isoformat()
    logs = st.session_state.setdefault("fitness_logs", {})
    today = logs.setdefault(today_key, {"workout": False, "walk": False, "water": False})
    st.markdown(f"## Welcome back{', athlete' if profile['level'] != 'New to training' else ''}.")
    st.caption(f"{profile['goal']}  ·  {profile['setting']}  ·  {profile['level']}")

    stats = st.columns(4)
    stats[0].metric("Weekly sessions", f"{profile['days']} days")
    stats[1].metric("Session target", f"{profile['duration']} min")
    stats[2].metric("Today’s check-ins", f"{sum(today.values())}/3")
    stats[3].metric("Training setup", profile["setting"])

    left, right = st.columns([1.3, 1])
    with left:
        st.markdown(f"<div class='hg-fitness-spotlight'><div><span class='hg-fitness-kicker'>YOUR PERSONAL GAME PLAN</span><h2>{html.escape(profile['goal'])}</h2><p>{html.escape(plan['focus'])}</p><span class='hg-fitness-tag'>{profile['days']} TRAINING DAYS · {profile['duration']} MIN</span></div><div class='hg-fitness-emblem'>✦</div></div>", unsafe_allow_html=True)
    with right:
        recent_cutoff = date.today().toordinal() - 6
        weekly_checkins = sum(
            1 for key, entry in logs.items()
            if key and date.fromisoformat(key).toordinal() >= recent_cutoff and entry.get("workout")
        )
        progress = min(100, round(weekly_checkins / max(1, profile["days"]) * 100))
        st.markdown(f"<div class='hg-fitness-panel hg-fitness-progress'><span class='hg-fitness-kicker'>WEEKLY MOMENTUM</span><h3>{weekly_checkins} of {profile['days']} movement check-ins</h3><div class='hg-progress-track'><div style='width:{progress}%'></div></div><p>Based on check-ins you record here. Your progress stays in this browser session.</p><div class='hg-progress-foot'><span>{progress}% of weekly target</span><span>{profile['days']} day goal</span></div></div>", unsafe_allow_html=True)

    if profile.get("note"):
        st.caption(f"Coach note: {profile['note']}")

    st.markdown("### Today’s momentum")
    task_col, schedule_col = st.columns([.9, 1.4])
    with task_col:
        st.markdown("<div class='hg-fitness-panel'><span class='hg-fitness-kicker'>DAILY CHECK-IN</span><h3>Small wins count.</h3><p>Keep your momentum visible.</p></div>", unsafe_allow_html=True)
        today["workout"] = st.checkbox("I moved or trained today", value=today["workout"], key=f"fitness_done_workout_{today_key}")
        today["walk"] = st.checkbox("I took a walk or stretch break", value=today["walk"], key=f"fitness_done_walk_{today_key}")
        today["water"] = st.checkbox("I checked in with my hydration", value=today["water"], key=f"fitness_done_water_{today_key}")
    with schedule_col:
        st.markdown("<div class='hg-fitness-panel'><span class='hg-fitness-kicker'>YOUR WEEKLY SPLIT</span><h3>Training schedule</h3></div>", unsafe_allow_html=True)
        schedule_cols = st.columns(min(3, len(plan["schedule"])))
        for index, (day, session) in enumerate(plan["schedule"]):
            with schedule_cols[index % len(schedule_cols)]:
                note = "Easy pace · move and recover" if any(kind in session.lower() for kind in ("cardio", "walk", "mobility")) else f"{profile['duration']} min · {plan['equipment']}"
                st.markdown(f"<div class='hg-fitness-session'><span>{day.upper()}</span><strong>{html.escape(session)}</strong><small>{note}</small></div>", unsafe_allow_html=True)
                if session in plan["moves"]:
                    with st.expander(f"View {session.lower()}"):
                        st.markdown("\n".join(f"- {move}" for move in plan["moves"][session]))
                        st.caption("Warm up gently for 5 minutes. Rest between sets. Keep every rep smooth and pain-free.")

    st.markdown("### Fuel your day")
    st.caption("Flexible meal inspiration, not a prescribed diet. Adjust portions to your appetite, culture and needs.")
    meal_cols = st.columns(4)
    for col, label, meal in zip(meal_cols, ["Breakfast", "Lunch", "Dinner", "Snack"], plan["meals"]):
        with col:
            st.markdown(f"<div class='hg-fitness-meal'><span>{label.upper()}</span><p>{html.escape(meal)}</p></div>", unsafe_allow_html=True)
    st.markdown("<div class='hg-fitness-footnote'>A balanced meal can include a protein source, colorful produce and a satisfying grain or starchy food.</div>", unsafe_allow_html=True)

    st.markdown("### Ask your fitness partner")
    with st.form("fitness_coach_form"):
        question = st.text_input("What would make your plan easier today?", placeholder="Ask for a shorter workout, exercise swaps, or meal ideas")
        asked = st.form_submit_button("Get a coaching nudge")
    if asked:
        if not question.strip():
            st.warning("Write a question first and I’ll help you think through it.")
        else:
            q = question.lower()
            if any(term in q for term in ["injur", "pain", "chest", "dizzy", "medical", "pregnan", "condition"]):
                st.warning("I can't assess symptoms or injuries. Pause the activity and get advice from a qualified healthcare professional before exercising. Seek urgent help for severe or sudden symptoms.")
            elif any(term in q for term in ["short", "busy", "time"]):
                st.success("Try a 10-minute version: 2 easy rounds of chair squats, incline push-ups and glute bridges, then finish. A shorter session still counts.")
            elif any(term in q for term in ["food", "meal", "diet", "eat", "protein"]):
                st.success("Keep it simple: choose a protein you enjoy, pair it with a grain or starchy food, and add fruit or vegetables when available. Your meal ideas above are a good starting point.")
            elif any(term in q for term in ["begin", "start", "motivat", "hard", "habit"]):
                st.success("Make the first step tiny: put on your shoes and do a five-minute warm-up. You can decide what comes next after you start; consistency grows from manageable wins.")
            else:
                st.success(f"For your {profile['goal'].lower()} goal, keep today comfortable and repeatable. {plan['focus']} If you tell me whether you want a workout swap, a shorter session or a meal idea, I can narrow it down.")
    st.caption("Coaching nudges are rule-based suggestions in this prototype, not generated by a live fitness model.")
