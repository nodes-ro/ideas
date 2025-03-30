from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from model import db, Idea
from sqlalchemy import or_  # Import the "or_" function

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ideas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Needed for flash messages

# Initialize the SQLAlchemy instance with the app
db.init_app(app)

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
    else:
        all_ideas = Idea.query.order_by(Idea.timestamp.desc()).all()
    return render_template('ideas.html', ideas=all_ideas)

@app.route('/idea/<unique_hash>')
def idea_detail(unique_hash):
    idea = Idea.query.filter_by(unique_hash=unique_hash).first()
    if idea is None:
        return render_template('404_custom.html'), 404
    return render_template('idea_detail.html', idea=idea)


from flask import jsonify


from flask import jsonify, request
from model import db, Idea

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

    if vote_type == 'up':
        idea.up_votes += 1
    elif vote_type == 'down':
        idea.down_votes += 1
    else:
        return jsonify(status="error", message="Invalid vote type."), 400

    try:
        db.session.commit()
    except Exception as e:
        # Log the error e for debugging if needed.
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


if __name__ == '__main__':
    # Create the database tables if they don't exist
    with app.app_context():
        db.create_all()
    app.run(debug=True,port=5005)