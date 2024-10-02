from openai import OpenAI
import os
import json
from flask import Flask, render_template, request
import markdown

app = Flask(__name__)

apikey = os.environ["OPENAI_API_KEY"]
client = OpenAI(api_key=apikey)

def load_prompts(path):
    with open(path, 'r') as file:
        prompts = json.load(file)
    return prompts

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

def generate_feedback(seniority_level, input_comment):
    prompts = load_prompts('prompts.json')
    if seniority_level == 1:
        prompt = prompts["senior-to-junior"] + "\n" + prompts["addendum"].format(input_comment=input_comment, factors=prompts["factors"])
    elif seniority_level == 2:
        prompt = prompts["peer-to-peer"] + "\n" + prompts["addendum"].format(input_comment=input_comment, factors=prompts["factors"])
    else:
        prompt = f"Provide constructive feedback on the following comment: {input_comment}"
    
    return prompt

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        input_comment = request.form['comment']
        seniority_level = int(request.form['seniority_level'])
        feedback_prompt = generate_feedback(seniority_level, input_comment)
        feedback = get_openai_response(feedback_prompt)
        feedback_html = markdown.markdown(feedback)
        return render_template('index.html', feedback=feedback_html)

    return render_template('index.html', feedback=None)

if __name__ == "__main__":
    app.run(debug=True)