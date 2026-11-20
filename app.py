
import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="📚",
    layout="wide"
)

# Initialize Gemini
api_key = os.getenv("GEMINI_API_KEY")

# Application title
st.title("📚 AI Study Buddy")
st.subheader("Your Personal AI Revision Assistant")

st.write(
    "Upload your study notes or paste your chapter. "
    "AI will create a quick revision pack for you!"
)

st.divider()

# Sidebar
with st.sidebar:
    st.title("📖 About")
    st.write("AI Study Buddy helps students revise faster.")
    st.write("Features:")
    st.write("✅ Notes Summary")
    st.write("✅ MCQ Quiz Generator")
    st.write("✅ Key Terms")
    st.write("✅ PDF Upload")

# Notes input
st.header("📝 Enter Your Study Notes")

notes = st.text_area(
    "Paste your notes here:",
    height=250,
    placeholder="Paste your chapter or study notes here..."
)

# PDF upload
st.header("📂 Or Upload Your PDF")

uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type=["pdf"]
)

# Generate button
if st.button("🚀 Generate Revision Pack", use_container_width=True):

    # Check API key
    if not api_key:
        st.error("Gemini API key not found. Please configure your .env file.")

    else:
        # Read PDF
        extracted_text = ""

        if uploaded_file is not None:
            try:
                reader = PdfReader(uploaded_file)

                for page in reader.pages:
                    extracted_text += page.extract_text() or ""

            except Exception as e:
                st.error(f"Unable to read PDF: {e}")
                st.stop()

        # Select input
        final_notes = extracted_text if uploaded_file else notes

        # Validate notes
        if not final_notes.strip():
            st.warning("Please paste notes or upload a PDF.")
        
        elif len(final_notes) > 30000:
            st.warning(
                "Your notes are too long. Please use a shorter "
                "text or PDF (maximum 30,000 characters)."
            )

        else:
            try:
                with st.spinner("🤖 AI is preparing your revision pack..."):

                    client = genai.Client(api_key=api_key)

                    prompt = f"""
                    You are an expert AI Study Assistant.

                    Analyze the following study notes and
                    create a revision pack.

                    Follow these instructions:

                    1. SUMMARY:
                    Write 5 to 6 important bullet points.

                    2. MULTIPLE CHOICE QUESTIONS:
                    Generate exactly 5 MCQ questions.
                    Each question must have 4 options (A, B, C, D).
                    Give the correct answer.
                    Give a short explanation.

                    3. KEY TERMS:
                    Identify exactly 3 important terms.
                    Explain each in simple language.

                    Important:
                    - Use only information supported by the notes.
                    - Do not invent facts.
                    - Keep the language simple and student-friendly.
                    - If information is missing, mention it.

                    Study Notes:
                    {final_notes}

                    Format the response using these headings:

                    ## 📌 Summary
                    ## 🧠 Multiple Choice Questions
                    ## 🔑 Key Terms
                    """

                    response = client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=prompt
                    )

                    result = response.text

                # Display output
                st.success("Revision Pack Generated Successfully!")

                st.divider()

                st.header("📌 Your Revision Pack")

                tab1, tab2, tab3 = st.tabs(
                    ["📌 Summary", "🧠 MCQ Quiz", "🔑 Key Terms"]
                )

                # Extract sections for display
                import re

                def get_section(text, heading, next_heading):
                    pattern = (
                        rf"{heading}\s*(.*?)(?={next_heading}|$)"
                    )
                    match = re.search(
                        pattern,
                        text,
                        flags=re.IGNORECASE | re.DOTALL
                    )
                    return match.group(1).strip() if match else ""

                summary = get_section(
                    result,
                    r"##\s*📌?\s*Summary",
                    r"##\s*🧠"
                )

                quiz = get_section(
                    result,
                    r"##\s*🧠\s*Multiple Choice Questions",
                    r"##\s*🔑"
                )

                terms = get_section(
                    result,
                    r"##\s*🔑\s*Key Terms",
                    r"(?!)"
                )

                with tab1:
                    st.markdown(summary or result)

                with tab2:
                    st.markdown(quiz or "Quiz section unavailable.")

                with tab3:
                    st.markdown(terms or "Key terms unavailable.")

                # Download revision pack
                st.divider()

                st.download_button(
                    label="📥 Download Revision Pack",
                    data=result,
                    file_name="AI_Study_Revision_Pack.md",
                    mime="text/markdown"
                )

            except Exception as e:
                st.error(f"Something went wrong: {e}")

# Footer
st.divider()

st.markdown(
    "<center>Made with ❤️ using Python, Streamlit and Gemini AI</center>",
    unsafe_allow_html=True
)