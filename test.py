from openai import OpenAI
from github import Github
import os
import json
from flask import Flask, render_template, request
import markdown

app = Flask(__name__)

openai_apikey = os.environ["OPENAI_API_KEY"]
github_apikey = os.environ["GITHUB_API_TOKEN"]
client = OpenAI(api_key=openai_apikey)
github = Github(github_apikey)

def load_prompts(path):
    with open(path, 'r') as file:
        prompts = json.load(file)
    return prompts

def get_pull_request_comments(repo_name):
    repo = github.get_repo(repo_name)
    pull_requests = repo.get_pulls(state='all')
    comments = []

    for pr in pull_requests:
        for comment in pr.get_review_comments():
            comments.append(comment.body)

    if comments == False:
        comments.append['No comments found.']
    return comments

def analyze_sentiment(comment):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "As a language model, your goal is to help with code review sentiment analysis."},
            {
                "role": "user",
                "content": f"Begin your response with two line breaks. Analyze the following code review comment:\n\n'{comment}'\n\n Rate each of the following from 1 to 5: Professionalism and Tone. Constructive nature. Use of code snippets. At the end provide an improved comment, followed by two line breaks."
            }
        ]
    )

    return completion.choices[0].message.content

@app.route("/", methods=["GET", "POST"])
def index():
    feedback_html = None
    if request.method == "POST":
        repo_name = request.form['repo_name']
        comments = get_pull_request_comments(repo_name)
        sentiment_results = {}
        for comment in comments:
            sentiment = analyze_sentiment(comment)
            sentiment_results[comment] = sentiment
        
        feedback = "\n".join([f"Comment: {comment}\nSentiment Analysis: {sentiment}" for comment, sentiment in sentiment_results.items()])
        feedback_html = markdown.markdown(feedback)
        
    return render_template('index.html', feedback=feedback_html)

if __name__ == "__main__":
    app.run(debug=True)