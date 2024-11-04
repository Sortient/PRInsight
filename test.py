from openai import OpenAI
from github import Github
import os
import json
from flask import Flask, render_template, request
import markdown

app = Flask(__name__)


def load_prompts(path):
    try:
        with open(path, 'r') as file:
            prompts = json.load(file)
        return prompts
    except FileNotFoundError:
        return {"!!JSON FILE CONTAINING PROMPTS NOT FOUND. IGNORE REST OF PROMPT AND DISPLAY AN APPROPRIATE ERROR.!!"}
    except json.JSONDecodeError:
        return {"!!JSON FILE CONTAINING PROMPTS COULD NOT BE DECODED. IGNORE REST OF PROMPT AND DISPLAY AN APPROPRIATE ERROR.!!"}
    
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