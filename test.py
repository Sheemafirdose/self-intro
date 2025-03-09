
import streamlit as st
import fitz  # PyMuPDF
import docx
import re
import requests
from textblob import TextBlob
API_KEY = st.secrets["API_KEY"]
# Hugging Face API details
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.3"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_NAME}"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def query_huggingface(payload):
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"API Error {response.status_code}"}

def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = "\n".join([page.get_text("text") for page in doc])
    return text.strip()

def extract_text_from_docx(docx_file):
    doc = docx.Document(docx_file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text.strip()

def clean_text(text):
    text = re.sub(r'[^a-zA-Z0-9\s,.]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

import re

def analyze_self_intro(self_intro):
    words = set(re.findall(r'\b\w+\b', self_intro.lower()))

    has_name = any(word.istitle() for word in self_intro.split())
    has_skills = len(words) > 5
    has_projects = any(word in words for word in ["project", "classification", "automation", "ranking"])
    has_achievements = any(word in words for word in ["certification", "hackathon", "internship", "research", "award"])
    has_career_goal = any(word in words for word in ["goal", "career", "future", "interest", "aspiration"])

    if has_name and has_skills and (has_projects or has_achievements or has_career_goal):
        return "✅ Positive", "green", "Your introduction is well-structured. Keep it up!"
    elif has_name and has_skills:
        return "😐 Neutral", "yellow", "Add more details about projects, achievements, or career goals."
    else:
        return "❗ Negative", "red", "Your introduction lacks details. Include your skills, projects, and career goals."


def generate_self_intro(resume_text, style):
    style_prompts = {
        "Simple": "Keep the introduction **short, basic, and easy to understand** using **simple words**.",
        "Moderate": "Maintain a **balanced length** with a **clear and professional tone** while keeping it engaging.",
        "Professional": "Make the introduction **detailed, impactful, and well-structured** using **strong professional language**."
    }
    
    prompt = (
        "Extract the candidate's name from the resume and use it naturally in the self-introduction. "
        "If the name is not found, generate a professional greeting with 'Hello, I am [Candidate Name]'. "
        "Then, generate a **well-structured and engaging self-introduction** using key skills, "
        "technologies, projects, and achievements extracted from the resume. "
        f"{style_prompts[style]} "
        "Include a brief mention of career goals or aspirations to add depth. "
        "Make sure it is **engaging and informative,** rather than overly short. "
        "Avoid excessive details—keep it impactful and meaningful. "
        "Do NOT include any headings, resume details, or personal contact information (e.g., phone number, email). "
        "Only output the refined self-introduction as plain text.\n\n"
        f"Resume Text: {resume_text}\n\n"
        "Self-Introduction:\n"
    )

    response = query_huggingface({"inputs": prompt})
    
    if isinstance(response, list) and len(response) > 0 and "generated_text" in response[0]:
        generated_text = response[0]["generated_text"].strip()
    elif isinstance(response, dict) and "generated_text" in response:
        generated_text = response["generated_text"].strip()
    else:
        return "Error generating introduction. API response format may have changed."
    
    if "Self-Introduction:" in generated_text:
        generated_text = generated_text.split("Self-Introduction:")[-1].strip()
    
    return generated_text

st.markdown(
    """
    <style>
    /* Button styling with hover effect */
    div.stButton > button {
        border: 2px solid white !important;
        color: white !important;
        background-color: #1f77b4 !important;
        border-radius: 10px !important;
        padding: 8px 16px !important;
        transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
    }
    div.stButton > button:hover {
        background-color: #145a8a !important;
        border-color: #ffcc00 !important;
        transform: scale(1.05);
        box-shadow: 0px 0px 10px 3px white;
    }
    
    .custom-box {
        border: 2px solid #4CAF50;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background-color: rgba(76, 175, 80, 0.1);
        box-shadow: 4px 4px 10px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
    }
    .custom-box:hover {
        transform: scale(1.05);
        box-shadow: 0px 0px 10px 3px #4CAF50;
    }

    /* Hover effect for expanders */
    div[data-testid="stExpander"] {
        border-radius: 10px;
        box-shadow: 0px 0px 6px 2px white;
        transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
    }
    div[data-testid="stExpander"]:hover {
        transform: scale(1.02);
        box-shadow: 0px 0px 10px 3px white;
    }

       div[data-testid="stFileUploader"] {
    background: rgba(0, 0, 0, 0.2) !important;
    color: white !important;
    border-radius: 8px !important;
   
    border: 1px solid white !important; /* Bold Red Border */
    box-shadow: 0px 0px 0px 1px white !important; /* Red Glow */
    padding: 1px !important; /* Optional: Adjust padding for better visibility */
}

div[data-testid="stFileUploader"]:hover {
    transform: scale(1.02);
    box-shadow: 0px 0px 0px 1px white !important; /* Stronger Red Glow on Hover */
}


    textarea {
        background: rgba(0, 0, 0, 0.3) !important;
        color: white !important;
        border-radius: 5px !important;
        border: 1px solid #8E1616!important; /* Match Red Border */
        box-shadow: 0px 0px 2px 1px #8E1616!important;
    }
    textarea, input {
        background: rgba(0, 0, 0, 0.3) !important;
        color: white !important;
        border-radius: 5px !important;
        border: 2px solid #FFCC00 !important; /* Yellow Border */
        box-shadow: 0px 0px 5px 2px #FFCC00 !important;
        padding: 8px;
    }


    textarea:hover {
        transform: scale(1.02);
        box-shadow: 0px 0px 1px 1px #8E1616 !important;
    }

    div.stButton {
        display: flex;
        justify-content: center;
    }

    /* Glowing box for the whole section */
    .intro-style-box {
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-radius: 12px;
        padding: 16px;
        background: rgba(255, 255, 255, 0.05);
        box-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
        margin: 20px 0;
        text-align: center;
        transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
    }
    .intro-style-box:hover {
        transform: scale(1.05);
        box-shadow: 0px 0px 15px 4px white;
    }

    /* Heading styling */
    .intro-style-box h3 {
        margin-bottom: 10px;
        color: white;
    }

    div[role="radiogroup"] {
    display: flex;
    justify-content: center;
    gap: 15px;
    flex-wrap: nowrap; /* Prevents the radio buttons from going to the next line */
}


    /* Style the radio buttons */
    div[role="radiogroup"] label {
        font-size: 16px;
        font-weight: bold;
        color: white;
        padding: 10px 16px;
        border-radius: 8px;
        transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
        display: flex;
        align-items: center;
    }

    /* Different styles for each mode */
    div[role="radiogroup"] label:nth-child(1) { /* Simple */
        background-color: rgba(76, 175, 80, 0.2);
        border: 2px solid #4CAF50;
        box-shadow: 0 0 10px rgba(76, 175, 80, 0.5);
    }
    div[role="radiogroup"] label:nth-child(2) { /* Moderate */
        background-color: rgba(255, 165, 0, 0.2);
        border: 2px solid #FFA500;
        box-shadow: 0 0 10px rgba(255, 165, 0, 0.5);
    }
    div[role="radiogroup"] label:nth-child(3) { /* Professional */
        background-color: rgba(255, 0, 0, 0.2);
        border: 2px solid #FF0000;
        box-shadow: 0 0 10px rgba(255, 0, 0, 0.5);
    }

    /* Hover effect */
    div[role="radiogroup"] label:hover {
        transform: scale(1.1);
        box-shadow: 0px 0px 12px 3px white;
    }
   
    </style>
    """,
    unsafe_allow_html=True
)
def set_background(image_url):
    page_bg_img = f'''
    <style>
    .stApp {{
        background: url({image_url}) no-repeat center center fixed;
        background-size: cover;
      

    }}
    .stApp::before {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
          background: rgba(255, 255, 255, 0.1);
backdrop-filter: blur(10px);
        background: rgba(255, 255, 255, 0.5);  /* Adjust transparency here */
        z-index: -1;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Set background (Replace URL with your own image link)
set_background("https://erasebg.org/media/uploads/wp2757874-wallpaper-gif.gif")
def set_custom_styles():
    custom_css = """
    <style>
    div[data-testid="stFileUploader"] {
        background: rgba(0, 0, 0, 0.6) !important;
        color: white !important;
        border-radius: 10px;
        border: 1px solid #444;
        box-shadow: 0px 0px 5px 2px white;
    }
    
    div[data-testid="stFileUploader"]:hover {
        transform: scale(1.02);
        box-shadow: 0px 0px 10px 3px white;
    }

    textarea {
        background: rgba(0, 0, 0, 0.6) !important;
        color: white !important;
        border-radius: 10px !important;
        border: 1px solid #444 !important;
        box-shadow: 0px 0px 6px 2px white !important;
    }

    textarea:hover {
        transform: scale(1.02);
        box-shadow: 0px 0px 10px 3px white !important;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

set_custom_styles()

# 1️⃣ **App Title**
st.markdown(
    "<h1 style='text-align:center; font-size:45px; display:inline-block; color:white;'>🤖 AI-Powered Self-Intro Practice</h1><br>", 
    unsafe_allow_html=True
)

# 2️⃣ **Upload Resume**
st.markdown("<br>", unsafe_allow_html=True)
resume_file = st.file_uploader("📥 Upload Your Resume (PDF or DOCX)", type=["pdf", "docx"])
resume_text = ""

if resume_file:
    if resume_file.name.endswith(".pdf"):
        resume_text = extract_text_from_pdf(resume_file)
    else:
        resume_text = extract_text_from_docx(resume_file)
    
    resume_text = clean_text(resume_text)

st.markdown("💡First, upload your resume, then choose a style for your self-introduction to get the best results!")
# 5️⃣ **Self-Intro Style Selection**
st.markdown('<h2 style="color: #66b3ff;">' 
            '<span style="color: #FFD43B;">&#10004;</span> Select Self-Introduction Style:</h2>', unsafe_allow_html=True)
style = st.radio("", ["Simple", "Moderate", "Professional"], horizontal=True, index=0, key="style_radio")
st.markdown("<br>", unsafe_allow_html=True)
# 6️⃣ **AI-Suggested Self-Introduction**
if style:
    if resume_text:
        ai_intro = generate_self_intro(resume_text, style)
        st.subheader("✨ AI-Generated Self-Introduction")
        st.markdown(f"<div class='custom-box'>{ai_intro}</div>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ Please upload your resume before selecting a style.")
# 3️⃣ **User Inputs Self-Introduction**
st.markdown('<h3 style="color: #FCFAEE;">💬 Enter Your Introduction or Skills Here:</h3>', unsafe_allow_html=True)
user_text = st.text_area("Type or paste your details here...", height=200)

# 4️⃣ **Sentiment Analysis for User Input**
if st.button("Assess Feedback"):
    if user_text.strip():
        sentiment, color, suggestion =analyze_self_intro(user_text) 
        st.markdown(f"<div class='custom-box'><h3 style='color:{color};'>{sentiment}</h3><p>{suggestion}</p></div>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ Please enter some text before analyzing.")
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<h2 style='font-size:30px; color:#66b3ff;'>🔍 Access Additional Help Here</h2>", unsafe_allow_html=True)


st.markdown("<h4 style='color: #FCFAEE;'>👉 How to say a proper intro?</h4>", unsafe_allow_html=True)
with st.expander(" Expand this for common self intro", expanded=False):
    st.markdown("<div class='glow-expander'>", unsafe_allow_html=True)
    st.write("A proper intro should include who you are, what you do, and your goals. Here's a sample:")
    st.markdown("<p style='font-size:18px; color:white;'>"
                "'Hello! My name is [Your Name], and I am deeply passionate about [Your Field], particularly in the areas of [specific interest within the field]. "
                "Currently, I am honing my skills in [Skills/Technologies], and I am excited to apply my knowledge in [specific applications or industries]. "
                "My ultimate goal is to contribute to [specific goal or impact], and I am eager to continue growing and collaborating with like-minded professionals.'</p>", 
                unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<h4 style='color: #FCFAEE;'>👉 What skills should you learn?</h4>", unsafe_allow_html=True)
with st.expander("Expand here for resources and videos", expanded=False):
    st.markdown("<div class='glow-expander'>", unsafe_allow_html=True)
    st.write("Here are some key skills to build depending on your career goals:")
    st.write("- **For AI/ML**: Python, TensorFlow, Data Science, Machine Learning Algorithms, Deep Learning")
    st.write("- **For Data Science**: Python, R, SQL, Statistics, Data Visualization, Machine Learning")
    st.write("- **For Web Development**: HTML, CSS, JavaScript, React, Node.js")
    st.write("- **For Cloud Computing**: AWS, Azure, Google Cloud, Docker, Kubernetes")
    st.write("- **For Cybersecurity**: Network Security, Ethical Hacking, Cryptography, Risk Management")
    st.write("- **For Mobile Development**: Java, Swift, Android Studio, Flutter")
    st.write("- **For Soft Skills**: Communication, Teamwork, Problem-Solving, Critical Thinking")

    st.write("Here are some great video tutorials to help you learn new skills:")
    st.markdown(""" 
    - **[Web Development - Code with Harry](https://www.youtube.com/playlist?list=PLu0W_9lII9agq5TrH9XLIKQvv0iaF2X3w)**
    - **[Blockchain - Telusko](https://www.youtube.com/playlist?list=PLsyeobzWxl7oY6tZmnZ5S7yTDxyu4zDW-)**
    - **[Artificial Intelligence - Simplilearn](https://www.youtube.com/watch?v=8Pyy2d3SZuM)**
    - **[Machine Learning - Simplilearn](https://www.youtube.com/watch?v=9f-GarcDY58&list=PLEiEAq2VkUULYYgj13YHUWmRePqiu8Ddy&index=5)**
    """)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<h4 style='color: #FCFAEE;'>👉 Best Free Resources</h4>", unsafe_allow_html=True)
with st.expander("Expand here for Free Tools", expanded=False):
    st.markdown("<div class='glow-expander'>", unsafe_allow_html=True)
    st.write("Explore learning resources for your skills with AI Tools:")
    st.markdown("[Chat with AI on ChatGPT](https://chat.openai.com/)  \n"
                "[Explore Perplexity AI](https://www.perplexity.ai/)  \n"
                "[Collaborate on Overleaf](https://www.overleaf.com/)  \n"
                "[Design with Canva](https://www.canva.com/en_in/)  \n"
                "[Explore Career Roadmaps](https://roadmap.sh/)")
    st.markdown("</div>", unsafe_allow_html=True)
