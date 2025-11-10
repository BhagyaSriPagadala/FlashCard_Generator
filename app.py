from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import pdfplumber
import docx2txt
import os
import tempfile
import json
import time

app = Flask(__name__)
CORS(app)

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyDtFrvZceExzYVdLMDf4JAf0znBccCkgq8"  # Replace with your actual API key
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

def extract_text_from_pdf(file_path):
    """Extract text from PDF using pdfplumber"""
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error extracting PDF: {e}")
    return text

def extract_text_from_docx(file_path):
    """Extract text from DOCX using docx2txt"""
    try:
        text = docx2txt.process(file_path)
        return text
    except Exception as e:
        print(f"Error extracting DOCX: {e}")
        return ""

def agentic_flashcard_generation(text, difficulty):
    """
    Multi-step agentic reasoning chain for flashcard generation
    """
    try:
        # Step 1: Analyze text structure and complexity
        print("Step 1: Analyzing document structure...")
        analysis_prompt = f"""
        Analyze the following text and provide:
        1. Main topics covered
        2. Complexity level
        3. Key concepts that should be highlighted
        
        Text:
        {text[:3000]}  # Limit to first 3000 chars for analysis
        
        Provide a structured analysis.
        """
        
        analysis = model.generate_content(analysis_prompt)
        print(f"Analysis complete: {analysis.text[:200]}...")
        
        # Step 2: Plan flashcard extraction strategy
        print("Step 2: Planning flashcard strategy...")
        planning_prompt = f"""
        Based on this analysis:
        {analysis.text}
        
        Create a plan to generate {difficulty} difficulty flashcards from the document.
        Consider:
        - How many flashcards to generate (Easy: 5-8, Medium: 8-12, Hard: 12-15)
        - What type of questions to ask (Easy: definitions, Medium: concepts, Hard: application/analysis)
        - How to structure questions for {difficulty} level
        
        Provide a clear extraction strategy.
        """
        
        plan = model.generate_content(planning_prompt)
        print(f"Planning complete: {plan.text[:200]}...")
        
        # Step 3: Generate flashcards
        print("Step 3: Generating flashcards...")
        generation_prompt = f"""
        Based on this plan:
        {plan.text}
        
        Generate flashcards from the following text at {difficulty} difficulty level:
        {text}
        
        Requirements:
        - {difficulty} level: {"Focus on key definitions and basic concepts" if difficulty == "Easy" else "Focus on understanding and relationships" if difficulty == "Medium" else "Focus on application, analysis, and critical thinking"}
        - Questions should be clear and specific
        - Answers should be comprehensive but concise
        - Each flashcard should test one key concept
        
        Return ONLY a valid JSON array in this exact format:
        [
          {{"question": "What is X?", "answer": "X is..."}},
          {{"question": "How does Y work?", "answer": "Y works by..."}}
        ]
        
        Return ONLY the JSON array, no additional text.
        """
        
        flashcards_response = model.generate_content(generation_prompt)
        flashcards_text = flashcards_response.text.strip()
        
        # Clean up response to extract JSON
        if "```json" in flashcards_text:
            flashcards_text = flashcards_text.split("```json")[1].split("```")[0].strip()
        elif "```" in flashcards_text:
            flashcards_text = flashcards_text.split("```")[1].split("```")[0].strip()
        
        flashcards = json.loads(flashcards_text)
        print(f"Generated {len(flashcards)} flashcards")
        
        # Step 4: Evaluate flashcards
        print("Step 4: Evaluating flashcards...")
        evaluation_prompt = f"""
        Evaluate these flashcards for:
        1. Clarity of questions
        2. Accuracy of answers
        3. Appropriate difficulty level ({difficulty})
        4. Completeness
        
        Flashcards:
        {json.dumps(flashcards, indent=2)}
        
        Respond with:
        - "APPROVED" if flashcards are good
        - "IMPROVE: [specific issues]" if they need refinement
        """
        
        evaluation = model.generate_content(evaluation_prompt)
        evaluation_text = evaluation.text.strip()
        print(f"Evaluation: {evaluation_text[:200]}...")
        
        # Step 5: Refine if needed
        if "IMPROVE" in evaluation_text.upper():
            print("Step 5: Refining flashcards...")
            refinement_prompt = f"""
            Improve these flashcards based on this feedback:
            {evaluation_text}
            
            Original flashcards:
            {json.dumps(flashcards, indent=2)}
            
            Return ONLY a valid JSON array with improved flashcards in the same format:
            [
              {{"question": "...", "answer": "..."}}
            ]
            
            Return ONLY the JSON array, no additional text.
            """
            
            refined_response = model.generate_content(refinement_prompt)
            refined_text = refined_response.text.strip()
            
            # Clean up response
            if "```json" in refined_text:
                refined_text = refined_text.split("```json")[1].split("```")[0].strip()
            elif "```" in refined_text:
                refined_text = refined_text.split("```")[1].split("```")[0].strip()
            
            flashcards = json.loads(refined_text)
            print(f"Refined to {len(flashcards)} flashcards")
        else:
            print("Step 5: Flashcards approved, no refinement needed")
        
        return flashcards
        
    except Exception as e:
        print(f"Error in agentic generation: {e}")
        # Fallback to simple generation
        return simple_flashcard_generation(text, difficulty)

def simple_flashcard_generation(text, difficulty):
    """Fallback simple generation if agentic approach fails"""
    try:
        prompt = f"""
        Generate {difficulty} difficulty flashcards from this text:
        {text}
        
        Return ONLY a valid JSON array:
        [
          {{"question": "What is X?", "answer": "X is..."}},
          {{"question": "How does Y work?", "answer": "Y works by..."}}
        ]
        """
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        return json.loads(response_text)
    except Exception as e:
        print(f"Error in simple generation: {e}")
        return [{"question": "Error generating flashcards", "answer": str(e)}]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_flashcards():
    try:
        # Get file and difficulty
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        difficulty = request.form.get('difficulty', 'Medium')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            file.save(tmp_file.name)
            tmp_path = tmp_file.name
        
        # Extract text based on file type
        if file.filename.lower().endswith('.pdf'):
            text = extract_text_from_pdf(tmp_path)
        elif file.filename.lower().endswith('.docx'):
            text = extract_text_from_docx(tmp_path)
        else:
            os.unlink(tmp_path)
            return jsonify({'error': 'Unsupported file format. Please upload PDF or DOCX'}), 400
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        if not text or len(text.strip()) < 50:
            return jsonify({'error': 'Could not extract sufficient text from document'}), 400
        
        # Generate flashcards using agentic approach
        flashcards = agentic_flashcard_generation(text, difficulty)
        
        return jsonify(flashcards)
        
    except Exception as e:
        print(f"Error in generate_flashcards: {e}")
        return jsonify({'error': str(e)}), 500
    


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)