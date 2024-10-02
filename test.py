from openai import OpenAI
import os
import tkinter
import re
from tkinter import messagebox
from flask import Flask, render_template, request

app = Flask(__name__)

apikey = os.environ["OPENAI_API_KEY"]
client = OpenAI(api_key=apikey)

def clean_markdown(text):
    # Remove common markdown symbols: *, _, `, and #
    clean_text = re.sub(r'[*_`#]', '', text)
    return clean_text

def get_openai_response(prompt):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "As a language model, your goal is to help with code review sentiment analysis."},
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return completion.choices[0].message.content

def show_feedback(feedback):
    root = tkinter.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showinfo("Generated Feedback", feedback)
    root.destroy()


def generate_feedback(seniority_level, input_comment):
    if seniority_level == 1:
        prompt = f"Rate the following comment from a senior developer to a junior developer on a pull request. Here's the comment: {input_comment}"
    elif seniority_level == 2:
        prompt = f"Rate the following comment from one senior developer to another senior developer on a pull request. Here's the comment: {input_comment}"
    else:
        prompt = f"Provide constructive feedback on the following comment: {input_comment}"
    
    prompt += " Rate the comment based on the following factors: Constructive, Professionalism and Tone, Use of Code Snippets (if the comment makes specific reference to code, otherwise leave this out). Provide a concise sample improved code review comment. It should be readable as one of many comments on a BitBucket diff, and not as an email. Also, do not use any exclamation marks or condescending language, particularly if between senior developers."
    return prompt

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        input_comment = request.form['comment']
        seniority_level = int(request.form['seniority_level'])

        # Generate feedback prompt
        feedback_prompt = generate_feedback(seniority_level, input_comment)

        # Get feedback from OpenAI API
        feedback = get_openai_response(feedback_prompt)

        # Clean the feedback from markdown
        clean_feedback = clean_markdown(feedback)

        # Render the feedback to the web page
        return render_template('index.html', feedback=clean_feedback)

    return render_template('index.html', feedback=None)

def main():
     # Get user input for the comment and seniority level
    input_comment = input("Enter comment to analyse:")
    seniority_level = 1

    # Generate the appropriate feedback prompt
    feedback_prompt = generate_feedback(seniority_level, input_comment)

    # Get feedback from OpenAI API
    feedback = get_openai_response(feedback_prompt)

    # Print the generated feedback
    print("\n\n\nGenerated Feedback:\n", feedback)
    formatted_text = clean_markdown(feedback)
    show_feedback(input_comment + "\n" + formatted_text)

# Standard Python entry point
if __name__ == "__main__":
    app.run(debug=True)