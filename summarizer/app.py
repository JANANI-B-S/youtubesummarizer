import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import pyttsx3

load_dotenv()  # Load all the environment variables
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


prompt = """You are a YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video, providing the important summary in a concise manner
within 250 words. Please provide the summary of the text given here:  """

# Function to extract video ID from YouTube URL
def extract_video_id(youtube_video_url):
    try:
        if 'v=' in youtube_video_url:
            video_id = youtube_video_url.split('v=')[1].split('&')[0]
            return video_id
        elif 'youtu.be/' in youtube_video_url:
            video_id = youtube_video_url.split('youtu.be/')[1].split('?')[0]
            return video_id
        else:
            st.error("Invalid YouTube URL format. Please provide a valid link.")
            return None
    except Exception as e:
        st.error(f"Error extracting video ID: {str(e)}")
        return None

# Function to get transcript details
def extract_transcript_details(youtube_video_url):
    try:
        video_id = extract_video_id(youtube_video_url)
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)

        transcript = ""
        for i in transcript_text:
            transcript += " " + i["text"]

        return transcript

    except Exception as e:
        st.error(f"Could not retrieve transcript: {str(e)}")
        return None

# Function to generate summary using Google Gemini Pro
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

# Function for text-to-speech
def text_to_speech(summary_text):
    engine = pyttsx3.init()
    audio_file = "summary_audio.mp3"
    engine.save_to_file(summary_text, audio_file)
    engine.runAndWait()
    return audio_file

# Streamlit UI
st.title("YouTube Transcript to Detailed Notes Converter")
st.write("Enter the YouTube video link below:")

youtube_link = st.text_input("YouTube Video Link:")

if youtube_link:
    video_id = extract_video_id(youtube_link)  # Extract video ID
    if video_id:  # Check if the video ID was successfully extracted
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button("Get Detailed Notes"):
    if video_id:  # Ensure we have a valid video ID
        transcript_text = extract_transcript_details(youtube_link)

        if transcript_text:
            summary = generate_gemini_content(transcript_text, prompt)

            # Process the summary to ensure clear formatting
            clear_summary = summary.replace('*', '') # Remove bullet points and add periods

            # Further clean up to ensure no leading symbols or bullet points
            clear_summary = clear_summary.replace('• ', '').replace('– ', '').strip()  # Remove any potential bullet points

            st.markdown("## Summary:")
            st.write(clear_summary)  # Display summary as plain text

            # Convert summary to speech without any special characters
            audio_file = text_to_speech(clear_summary)
            st.audio(audio_file, format='audio/mp3')  # Play audio in the app
            
            # Provide download link for audio file
            with open(audio_file, "rb") as f:
                st.download_button("Download Summary Audio", f, file_name="summary_audio.mp3")

