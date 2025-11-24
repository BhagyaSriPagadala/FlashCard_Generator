# FlashCard_Generator
An Agentic AI web app that analyzes text documents or user input and automatically generates AI-powered flashcards using Google’s Gemini API.
Built with Flask, HTML, CSS, and JavaScript, it provides an intuitive interface for learning and revising key concepts intelligently.

🌟 Features

🧩 Gemini AI Integration – Uses Google’s Generative AI to summarize and generate flashcards.

⚡ Agentic Reasoning – Dynamically adapts flashcard content based on difficulty or user preference.

🎨 Frontend in HTML/CSS/JS – Clean, minimal beige-themed design.

🔗 Flask Backend – Handles AI requests, text processing, and data flow.

🧰 Easy Deployment – Fully compatible with Hugging Face Spaces, Render, and local ngrok testing.

🗂️ Project Structure
📦 agentic-ai-flashcards/

 ┣ 📂 static/                # CSS, JS, images
 
 ┣ 📂 templates/             # HTML templates (Flask)
 
 ┣ 📜 app.py                 # Flask backend
 
 ┣ 📜 requirements.txt       # Dependencies
 
 ┣ 📜 Procfile               # Deployment entry for Render
 
 ┣ 📜 .gitignore             # Ignore venv, cache, etc.
 
 ┗ 📜 README.md              # Project overview

 🚀 Example Workflow

User uploads a .txt or .pdf file (or types text).

Chooses difficulty level (Easy / Medium / Hard).

Flask backend sends input to Gemini API.

Gemini model generates flashcards (Q&A style).

Frontend displays interactive flashcards for learning.



https://github.com/user-attachments/assets/de62133c-46ef-4a22-b4fb-5208c65f93a1



