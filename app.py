import streamlit as st
from pathlib import Path
from datetime import datetime
import uuid
import requests


# ==============================
# 1. PAGE CONFIGURATION
# ==============================

st.set_page_config(
    page_title="SMiShing Awareness and Detection Tool",
    layout="centered"
)


# ==============================
# 2. CUSTOM STYLE / COLOURS
# ==============================

st.markdown(
    """
    <style>
    .stApp {
        background-color: #F7F9FC;
    }

    h1 {
        color: #1B4965;
        text-align: center;
    }

    h2, h3 {
        color: #1B4965;
    }

    .stButton > button {
        background-color: #1B4965;
        color: white;
        border-radius: 10px;
        padding: 0.6em 1.2em;
        font-weight: bold;
        border: none;
    }

    .stButton > button:hover {
        background-color: #163A52;
        color: white;
    }

    div[data-testid="stMetric"] {
        background-color: #EAF4F8;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #D0E3EA;
    }

    div[data-testid="stInfo"] {
        border-radius: 12px;
    }

    div[data-testid="stWarning"] {
        border-radius: 12px;
    }

    div[data-testid="stError"] {
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ==============================
# 3. SCORING SETTINGS
# ==============================

MAX_RAW_SCORE = 80


# ==============================
# 4. SMS DETECTION TASKS
# ==============================

SMS_TASKS = [
    {
        "id": "sms01",
        "title": "SMS Message 1",
        "image_file": "sms01.png",
        "correct_answer": "Fake"
    },
    {
        "id": "sms02",
        "title": "SMS Message 2",
        "image_file": "sms02.png",
        "correct_answer": "Real"
    },
    {
        "id": "sms03",
        "title": "SMS Message 3",
        "image_file": "sms03.png",
        "correct_answer": "Fake"
    },
    {
        "id": "sms04",
        "title": "SMS Message 4",
        "image_file": "sms04.png",
        "correct_answer": "Real"
    },
    {
        "id": "sms05",
        "title": "SMS Message 5",
        "image_file": "sms05.png",
        "correct_answer": "Fake"
    },
    {
        "id": "sms06",
        "title": "SMS Message 6",
        "image_file": "sms06.png",
        "correct_answer": "Real"
    },
    {
        "id": "sms07",
        "title": "SMS Message 7",
        "image_file": "sms07.png",
        "correct_answer": "Fake"
    },
    {
        "id": "sms08",
        "title": "SMS Message 8",
        "image_file": "sms08.png",
        "correct_answer": "Real"
    },
    {
        "id": "sms09",
        "title": "SMS Message 9",
        "image_file": "sms09.png",
        "correct_answer": "Fake"
    },
    {
        "id": "sms10",
        "title": "SMS Message 10",
        "image_file": "sms10.png",
        "correct_answer": "Real"
    },
]


# ==============================
# 5. QUESTION LISTS
# ==============================

RSEBIS_QUESTIONS = [
    ("rsebis_q1", "I verify the URL before clicking any link contained in an SMS message."),
    ("rsebis_q2", "I use strong, unique passwords for each of my digital accounts."),
    ("rsebis_q3", "When I receive a suspicious SMS, I contact the purported sender via their official channel to verify its authenticity."),
    ("rsebis_q4", "I report suspicious or fraudulent SMS messages to my mobile carrier or relevant authorities."),
    ("rsebis_q5", "I regularly update my smartphone applications to prevent exposure to security vulnerabilities."),
    ("rsebis_q6", "I refrain from responding to SMS messages that request sensitive personal or financial information."),
]

PRIVACY_QUESTIONS = [
    ("privacy_q1", "I am concerned that information I share via my smartphone may be used against me."),
    ("privacy_q2", "I believe protecting my personal data is primarily my own responsibility."),
    ("privacy_q3", "I hesitate to share personal information with apps or services I am not familiar with."),
]

ATTENTION_QUESTIONS = [
    ("attention_q1", "I am able to maintain focus on tasks even in the presence of distractions."),
    ("attention_q2", "I read digital content carefully and completely before taking any action."),
    ("attention_q3", "I pay close attention to small details in messages, such as the sender's address and URL format."),
    ("attention_q4", "I think carefully before clicking on any link that comes from an unfamiliar source."),
]

EVALUATION_QUESTIONS = [
    ("eval_q1", "The tool was easy to use."),
    ("eval_q2", "The SMS examples looked realistic."),
    ("eval_q3", "The feedback helped me understand my weak points."),
    ("eval_q4", "The tool increased my awareness of smishing risks."),
    ("eval_q5", "I would recommend this tool to others."),
]


# ==============================
# 6. SCORING MAPS
# ==============================

FREQUENCY_5 = {
    "1 - Never": 1,
    "2 - Rarely": 2,
    "3 - Sometimes": 3,
    "4 - Often": 4,
    "5 - Always": 5,
}

LIKERT_5 = {
    "1 - Strongly Disagree": 1,
    "2 - Disagree": 2,
    "3 - Neutral": 3,
    "4 - Agree": 4,
    "5 - Strongly Agree": 5,
}

FREQUENCY_4 = {
    "1 - Never": 1,
    "2 - Sometimes": 2,
    "3 - Often": 3,
    "4 - Always": 4,
}

TRAINING_SCORE = {
    "Academic course or professional certification": 3,
    "Workplace / organisational training session": 2,
    "Self-directed learning": 1,
    "No cybersecurity training": 0,
}

VICTIM_SCORE = {
    "Yes, I realised only after the fact": 0,
    "Yes, I detected it before suffering any harm": 2,
    "No, this has never happened to me": 2,
    "I am not certain": 1,
}

ACTION_SCORE = {
    "Delete the message immediately without further action": 1,
    "Report it directly to my mobile carrier or relevant authorities": 2,
    "Verify the sender through official channels first, then report": 2,
    "Ignore it without deleting": 0,
    "Forward the link to another person to check": 0,
}

REPORT_KNOWLEDGE_SCORE = {
    "Yes, I know the complete reporting process": 2,
    "Partially, I know some steps but not all": 1,
    "No, I am unaware of how to report such messages": 0,
}


# ==============================
# 7. IMAGE HANDLING
# ==============================

def get_image_path(image_file):
    """
    This function makes image loading more flexible.

    It first tries:
    images/sms01.png

    If not found, it tries:
    sms01.png

    This helps if images were uploaded individually to GitHub.
    """

    path_inside_images_folder = Path("images") / image_file
    path_next_to_app = Path(image_file)

    if path_inside_images_folder.exists():
        return path_inside_images_folder

    if path_next_to_app.exists():
        return path_next_to_app

    return None


# ==============================
# 8. GOOGLE APPS SCRIPT STORAGE
# ==============================

def save_to_google_sheet_via_apps_script(row_data):
    """
    Send participant data from Streamlit to Google Apps Script.
    Google Apps Script saves the data in Google Sheets.
    """

    apps_script_url = st.secrets["apps_script"]["url"]
    secret_key = st.secrets["apps_script"]["secret_key"]

    payload = row_data.copy()
    payload["secret_key"] = secret_key

    response = requests.post(
        apps_script_url,
        json=payload,
        timeout=20
    )

    if response.status_code != 200:
        raise Exception(f"HTTP Error: {response.status_code}")

    result = response.json()

    if result.get("status") in ["success", "duplicate"]:
        return result

    raise Exception(result.get("message", "Unknown Apps Script error"))


# ==============================
# 9. HELPER FUNCTIONS
# ==============================

def calculate_score_out_of_100(total_raw_score):
    score_100 = (total_raw_score / MAX_RAW_SCORE) * 100
    return round(score_100, 2)


def get_recommendation(detection_score, total_score_100):
    if detection_score <= 4:
        detection_level = "High smishing vulnerability"
        advice = (
            "You should be very careful with SMS links. "
            "Always verify the sender through official channels before clicking."
        )
    elif detection_score <= 7:
        detection_level = "Moderate smishing vulnerability"
        advice = (
            "You identified some messages correctly, but you may still miss warning signs "
            "such as fake URLs, urgent language, or unknown senders."
        )
    else:
        detection_level = "Low smishing vulnerability"
        advice = (
            "You performed well in the SMS detection task. "
            "Continue checking sender names, URLs, and suspicious requests."
        )

    if total_score_100 < 50:
        awareness_level = "Low awareness"
    elif total_score_100 < 75:
        awareness_level = "Moderate awareness"
    else:
        awareness_level = "High awareness"

    reporting_advice = (
        '<br><br>'
        '<strong>Report suspicious SMS messages by forwarding them to the designated number '
        '<u>330330</u>.</strong>'
    )

    full_advice = advice + reporting_advice

    return detection_level, awareness_level, full_advice

def initialise_session_state():
    if "page" not in st.session_state:
        st.session_state.page = "welcome"

    if "participant_id" not in st.session_state:
        st.session_state.participant_id = str(uuid.uuid4())

    if "survey_data" not in st.session_state:
        st.session_state.survey_data = {}

    if "response_saved" not in st.session_state:
        st.session_state.response_saved = False

    if "saving_in_progress" not in st.session_state:
        st.session_state.saving_in_progress = False


def go_to_page(page_name):
    st.session_state.page = page_name
    st.rerun()


initialise_session_state()


# ==============================
# 10. WELCOME PAGE
# ==============================

def show_welcome_page():
    st.title("SMiShing Awareness and Detection Tool")

    st.subheader(
        "Exploring the Effect of Age on Smishing Vulnerability Among Saudi Users"
    )

    st.write(
        """
        Thank you for participating in this voluntary online survey. 
        The purpose of this study is to understand how smartphone users interact with 
        and make decisions about SMS text messages.
        """
    )

    st.info(
        """
        **Informed Consent Summary**

        - Your participation is entirely voluntary.
        - You may withdraw at any time.
        - All responses are anonymous and confidential.
        - No personally identifiable information will be collected.
        - Data will be used solely for academic research purposes.
        - By proceeding, you confirm you are 18 years of age or older.
        """
    )

    st.write(
        """
        **Instrument Description**

        - Estimated completion time: 10–15 minutes
        - Number of sections: 6
        - Question types: Multiple-choice, SMS classification tasks, and Likert scale
        - No questions about passwords, account credentials, or personal financial data
        """
    )

    st.warning(
        """
        **Ethical Approval Notice**

        This study has been reviewed and approved by the Institutional Review Board 
        at Newcastle University.

        Approval Number: 76424/2026
        """
    )
    st.markdown("""
    **Researcher Contact Details**

    **Researcher:** Sarah S. A. Alsubaiei  
    **Institution:** Newcastle University  
    **Email:** S.S.Alsubaiei2@newcastle.ac.uk
""")


    consent = st.checkbox(
        "I have read and understood the information above and agree to participate voluntarily."
    )

    if st.button("Begin Survey →", disabled=not consent):
        go_to_page("survey")


# ==============================
# 11. SURVEY PAGE
# ==============================

def show_survey_page():
    st.title("SMiShing Survey")

    with st.form("survey_form"):

        st.header("Section 1: Demographic Information")

        age_group = st.radio(
            "Q1. What is your age group?",
            [
                "18–24 years",
                "25–34 years",
                "35–44 years",
                "45–54 years",
                "55 years or older"
            ],
            index=None
        )

        gender = st.radio(
            "Q2. What is your gender?",
            [
                "Male",
                "Female",
                "Prefer not to say"
            ],
            index=None
        )

        education = st.radio(
            "Q3. What is your highest level of education?",
            [
                "Less than high school",
                "High school diploma",
                "Diploma / Bachelor's degree",
                "Master's degree",
                "Doctoral degree"
            ],
            index=None
        )

        occupation = st.radio(
            "Q4. What is your current occupation?",
            [
                "Student",
                "IT professional",
                "Administrative / Financial",
                "Healthcare / Education",
                "Self-employed / Business",
                "Not currently employed",
                "Other"
            ],
            index=None
        )

        smartphone_hours = st.radio(
            "Q5. How many hours per day do you spend using your smartphone?",
            [
                "Less than 2 hours",
                "2–4 hours",
                "4–6 hours",
                "More than 6 hours"
            ],
            index=None
        )

        st.header("Section 2: SMS Message Detection Task")

        sms_answers = {}
        sms_reasons = {}

        for number, task in enumerate(SMS_TASKS, start=1):
            st.subheader(f"{number}. {task['title']}")

            image_path = get_image_path(task["image_file"])

            if image_path is not None:
                st.image(str(image_path), use_container_width=True)
            else:
                st.warning(
                    f"Image not found: {task['image_file']}. "
                    "Please check that the image name is correct."
                )

            answer = st.radio(
                "Is this message real or fake?",
                ["Real", "Fake"],
                key=f"{task['id']}_answer",
                index=None
            )

            reason = st.text_area(
                "Why do you think it is real or fake? This question is required.",
                key=f"{task['id']}_reason",
                placeholder="Write your reason here..."
            )

            sms_answers[task["id"]] = answer
            sms_reasons[task["id"]] = reason

        st.header("Section 3: Digital Security Behaviour")

        rsebis_answers_text = {}
        rsebis_scores = {}

        for qid, question in RSEBIS_QUESTIONS:
            selected = st.radio(
                question,
                list(FREQUENCY_5.keys()),
                key=qid,
                index=None
            )

            rsebis_answers_text[qid] = selected
            rsebis_scores[qid] = FREQUENCY_5[selected] if selected is not None else None

        st.header("Section 4: Online Privacy Concerns")

        privacy_answers_text = {}
        privacy_scores = {}

        for qid, question in PRIVACY_QUESTIONS:
            selected = st.radio(
                question,
                list(LIKERT_5.keys()),
                key=qid,
                index=None
            )

            privacy_answers_text[qid] = selected
            privacy_scores[qid] = LIKERT_5[selected] if selected is not None else None

        st.header("Section 5: Cybersecurity Training and Reporting Behaviour")

        training = st.radio(
            "Q1. Have you ever received any formal cybersecurity training or education?",
            list(TRAINING_SCORE.keys()),
            index=None
        )

        victim = st.radio(
            "Q2. Have you ever been victimised by a SMiShing attack?",
            list(VICTIM_SCORE.keys()),
            index=None
        )

        action = st.radio(
            "Q3. When you identify a suspicious SMS, what action do you typically take?",
            list(ACTION_SCORE.keys()),
            index=None
        )

        report_knowledge = st.radio(
            "Q4. Do you know how to formally report a fraudulent SMS?",
            list(REPORT_KNOWLEDGE_SCORE.keys()),
            index=None
        )

        st.header("Section 6: Attention Control")

        attention_answers_text = {}
        attention_scores = {}

        for qid, question in ATTENTION_QUESTIONS:
            selected = st.radio(
                question,
                list(FREQUENCY_4.keys()),
                key=qid,
                index=None
            )

            attention_answers_text[qid] = selected
            attention_scores[qid] = FREQUENCY_4[selected] if selected is not None else None

        submitted = st.form_submit_button("Finish and See My Result")

    if submitted:

        missing_items = []

        demographic_answers = {
            "age_group": age_group,
            "gender": gender,
            "education": education,
            "occupation": occupation,
            "smartphone_hours": smartphone_hours,
        }

        for name, value in demographic_answers.items():
            if value is None:
                missing_items.append(name)

        for task in SMS_TASKS:
            task_id = task["id"]

            if sms_answers[task_id] is None:
                missing_items.append(f"{task_id}_answer")

            if sms_reasons[task_id].strip() == "":
                missing_items.append(f"{task_id}_reason")

        for qid, value in rsebis_scores.items():
            if value is None:
                missing_items.append(qid)

        for qid, value in privacy_scores.items():
            if value is None:
                missing_items.append(qid)

        if training is None:
            missing_items.append("training")

        if victim is None:
            missing_items.append("victim")

        if action is None:
            missing_items.append("action")

        if report_knowledge is None:
            missing_items.append("report_knowledge")

        for qid, value in attention_scores.items():
            if value is None:
                missing_items.append(qid)

        if missing_items:
            st.error(
                "Please answer all required questions, including the reason for each SMS message."
            )
            st.stop()

        detection_score = 0

        for task in SMS_TASKS:
            participant_answer = sms_answers[task["id"]]
            correct_answer = task["correct_answer"]

            if participant_answer == correct_answer:
                detection_score += 1

        rsebis_score = sum(rsebis_scores.values())
        privacy_score = sum(privacy_scores.values())

        training_score = (
            TRAINING_SCORE[training]
            + VICTIM_SCORE[victim]
            + ACTION_SCORE[action]
            + REPORT_KNOWLEDGE_SCORE[report_knowledge]
        )

        attention_score = sum(attention_scores.values())

        total_raw_score = (
            detection_score
            + rsebis_score
            + privacy_score
            + training_score
            + attention_score
        )

        total_score_100 = calculate_score_out_of_100(total_raw_score)

        row = {
            "participant_id": st.session_state.participant_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

            "age_group": age_group,
            "gender": gender,
            "education": education,
            "occupation": occupation,
            "smartphone_hours": smartphone_hours,

            "detection_score_out_of_10": detection_score,
            "rsebis_score_out_of_30": rsebis_score,
            "privacy_score_out_of_15": privacy_score,
            "training_score_out_of_9": training_score,
            "attention_score_out_of_16": attention_score,

            "total_raw_score_out_of_80": total_raw_score,
            "total_score_out_of_100": total_score_100,
        }

        for task in SMS_TASKS:
            task_id = task["id"]

            row[f"{task_id}_answer"] = sms_answers[task_id]
            row[f"{task_id}_correct_answer"] = task["correct_answer"]
            row[f"{task_id}_reason"] = sms_reasons[task_id]

        for qid in rsebis_scores:
            row[f"{qid}_answer"] = rsebis_answers_text[qid]
            row[f"{qid}_score"] = rsebis_scores[qid]

        for qid in privacy_scores:
            row[f"{qid}_answer"] = privacy_answers_text[qid]
            row[f"{qid}_score"] = privacy_scores[qid]

        row["training_answer"] = training
        row["victim_answer"] = victim
        row["action_answer"] = action
        row["report_knowledge_answer"] = report_knowledge

        for qid in attention_scores:
            row[f"{qid}_answer"] = attention_answers_text[qid]
            row[f"{qid}_score"] = attention_scores[qid]

        st.session_state.survey_data = row

        go_to_page("result")


# ==============================
# 12. RESULT AND EVALUATION PAGE
# ==============================

def show_result_page():
    st.title("Your Result")

    row = st.session_state.survey_data

    detection_score = row["detection_score_out_of_10"]
    total_raw_score = row["total_raw_score_out_of_80"]
    total_score_100 = row["total_score_out_of_100"]

    detection_level, awareness_level, advice = get_recommendation(
        detection_score,
        total_score_100
    )

    st.metric("SMS Detection Score", f"{detection_score}/10")
    st.metric("Raw Awareness Score", f"{total_raw_score}/80")
    st.metric("Final Awareness Score", f"{total_score_100}/100")

    st.subheader("Interpretation")
    st.write(f"**Detection level:** {detection_level}")
    st.write(f"**Awareness level:** {awareness_level}")

    st.subheader("Recommendation")
    st.markdown(
    f"""
    <div style="
        background-color: #EAF4F8;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #D0E3EA;
        color: #1B4965;
        font-size: 16px;
        line-height: 1.6;
    ">
        {advice}
    </div>
    """,
    unsafe_allow_html=True
)

    st.divider()

    if st.session_state.response_saved:
        st.success(
            "Thank you for taking part. Your response has been saved successfully."
        )
        st.info("You may now close this page.")
        st.stop()

    st.header("Tool Evaluation")

    st.write("Please answer these final questions about the tool.")

    with st.form("evaluation_form"):

        evaluation_answers_text = {}
        evaluation_scores = {}

        for qid, question in EVALUATION_QUESTIONS:
            selected = st.radio(
                question,
                list(LIKERT_5.keys()),
                key=qid,
                index=None
            )

            evaluation_answers_text[qid] = selected
            evaluation_scores[qid] = LIKERT_5[selected] if selected is not None else None

        save_button = st.form_submit_button(
            "Submit Final Response",
            disabled=st.session_state.saving_in_progress or st.session_state.response_saved
        )

    if save_button:

        missing_evaluation = []

        for qid, value in evaluation_scores.items():
            if value is None:
                missing_evaluation.append(qid)

        if missing_evaluation:
            st.error("Please answer all tool evaluation questions.")
            st.stop()

        final_row = row.copy()

        for qid in evaluation_scores:
            final_row[f"{qid}_answer"] = evaluation_answers_text[qid]
            final_row[f"{qid}_score"] = evaluation_scores[qid]

        st.session_state.saving_in_progress = True

        try:
            result = save_to_google_sheet_via_apps_script(final_row)

            st.session_state.response_saved = True
            st.session_state.saving_in_progress = False

            if result.get("status") == "duplicate":
                st.success(
                    "Thank you for taking part. Your response has already been saved successfully."
                )
            else:
                st.success(
                    "Thank you for taking part. Your response has been saved successfully."
                )

            st.info("You may now close this page.")
            st.balloons()
            st.stop()

        except Exception as error:
            st.session_state.saving_in_progress = False

            st.error(
                "There was a problem saving your response. Please contact the researcher."
            )

            st.write("Technical error:")
            st.code(str(error))


# ==============================
# 13. PAGE ROUTER
# ==============================

if st.session_state.page == "welcome":
    show_welcome_page()

elif st.session_state.page == "survey":
    show_survey_page()

elif st.session_state.page == "result":
    show_result_page()
