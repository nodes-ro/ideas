import json
import os

from flask import Flask, render_template, redirect, url_for, flash
from sqlalchemy import or_
from model import db, Idea
import openai
from flask_wtf.csrf import CSRFProtect
from flask import session, jsonify, request
from sqlalchemy import func

app = Flask(__name__)
client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ideas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key2'  # Needed for flash messages

# Initialize the SQLAlchemy instance with the app
db.init_app(app)
csrf = CSRFProtect(app)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/support')
def support():
    return render_template('support.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_idea', methods=['POST'])
def submit_idea():
    title = request.form['title']
    description = request.form['description']
    impact = request.form['impact']
    attribution = request.form['attribution']

    new_idea = Idea(title=title, description=description, impact=impact, attribution=attribution)
    db.session.add(new_idea)
    db.session.commit()

    flash('Thanks. Idea submitted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/ideas')
def ideas():
    order = request.args.get('order')
    if order == 'upvotes':
        all_ideas = Idea.query.order_by(Idea.up_votes.desc()).all()
    elif order == 'alphabetical':
        all_ideas = Idea.query.order_by(func.lower(Idea.title).asc()).all()
    else:
        all_ideas = Idea.query.order_by(Idea.timestamp.desc()).all()
    return render_template('ideas.html', ideas=all_ideas)

@app.route('/idea/<unique_hash>')
def idea_detail(unique_hash):
    idea = Idea.query.filter_by(unique_hash=unique_hash).first()
    if idea is None:
        return render_template('404_custom.html'), 404
    return render_template('idea_detail.html', idea=idea)



@app.route('/vote')
def vote():
    try:
        idea_id = int(request.args.get('idea_id'))
    except (TypeError, ValueError):
        return jsonify(status="error", message="Invalid idea ID."), 400

    vote_type = request.args.get('vote')
    idea = Idea.query.get(idea_id)

    if idea is None:
        return jsonify(status="error", message="Idea not found."), 404

    # Prevent multiple votes for the same idea within the same session.
    voted_key = f"voted_{idea_id}"
    if session.get(voted_key):
        return jsonify(status="error", message="You have already voted for this idea."), 403

    if vote_type == 'up':
        idea.up_votes += 1
    elif vote_type == 'down':
        idea.down_votes += 1
    else:
        return jsonify(status="error", message="Invalid vote type."), 400

    try:
        db.session.commit()
        # Mark the idea as voted in the session
        session[voted_key] = True
    except Exception as e:
        db.session.rollback()
        return jsonify(status="error", message="Database error."), 500

    return jsonify(
        status="success",
        message="Thanks for your vote!",
        up_votes=idea.up_votes,
        down_votes=idea.down_votes
    )


@app.route('/search')
def search():
    query = request.args.get('q', '')
    if query:
        # Search in title or description using case-insensitive matching
        results = Idea.query.filter(
            or_(
                Idea.title.ilike(f'%{query}%'),
                Idea.description.ilike(f'%{query}%')
            )
        ).order_by(Idea.timestamp.desc()).all()
    else:
        results = []
    return render_template('search_results.html', ideas=results, query=query)

@app.route("/ai_reply", methods=["GET"])
def ai_reply():
    # 1. start point for ai generation
    user_message = request.args.get("message", "").strip()
    if not user_message:
        return render_template("ai_reply.html", reply="No message provided.")
    return render_template("ai_loading.html", message=user_message)

async def ai_generate_idea(user_message):
    """Fetch AI response asynchronously with error handling and split output into title, description, impact, and attribution (default 'AI')."""
    craft_prompt = '''
    You are to generate a creative idea based on the user input. 
    The output must be a valid JSON object with exactly four keys:
      - "title": A concise title for the idea.
      - "description": A detailed description of the idea.
      - "impact": A clear outline of the benefits and impact of this idea.
      - "attribution": Set this field to "AI" by default.
    Important:
  - Your response must not contain any obscene, illegal, or harmful content.
  - If the user's input includes requests or terms that are obscene or illegal, instead of generating a creative idea, return a JSON object with the following values:
      "title": "Invalid Input",
      "description": "The provided input is not allowed.",
      "impact": "The provided input is not allowed.",
      "attribution": "User"
    Return nothing but the JSON.
    '''
    # Format the user's input
    user_input = f"Generate an idea based on this input: {user_message} Use the same language for the output as the input."

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": craft_prompt},
                {"role": "user", "content": user_input}
            ]
        )

        if response and response.choices and len(response.choices) > 0:
            content = response.choices[0].message.content
            try:
                # Parse the JSON from the AI response
                result = json.loads(content)
                # If the attribution key is missing, set it to "AI"
                if "attribution" not in result:
                    result["attribution"] = "AI"
                # Verify that all expected keys exist
                if all(key in result for key in ("title", "description", "impact", "attribution")):
                    return result
                else:
                    return {
                        "title": "Error",
                        "description": "Incomplete response. Expected keys not found.",
                        "impact": "",
                        "attribution": "AI"
                    }
            except Exception as json_e:
                return {
                    "title": "Error",
                    "description": f"Failed to parse JSON response: {str(json_e)}. Raw response: {content}",
                    "impact": "",
                    "attribution": "AI"
                }
        else:
            return {
                "title": "No Response",
                "description": "No response from AI model.",
                "impact": "",
                "attribution": "AI"
            }
    except openai.OpenAIError as e:
        return {
            "title": "API Error",
            "description": str(e),
            "impact": "",
            "attribution": "AI"
        }
    except Exception as e:
        return {
            "title": "Unexpected Error",
            "description": str(e),
            "impact": "",
            "attribution": "AI"
        }

@app.route("/fetch_ai_reply", methods=["POST"])
async def fetch_ai_reply():
    user_message = request.form.get("message", "").strip()  # Use request.form for POST
    if not user_message:
        return render_template("ai_reply.html", reply="No message provided.")
    ai_response = await ai_generate_idea(user_message)
    return render_template("ai_reply.html", reply=ai_response)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8005, debug=True)