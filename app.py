from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from model import db, Idea

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



@app.route('/vote')
def vote():
    idea_id = request.args.get('idea_id')
    vote_type = request.args.get('vote')
    idea = Idea.query.get(idea_id)
    if idea is None:
        flash("Idea not found.", "error")
        return redirect(url_for('ideas'))
    if vote_type == 'up':
        idea.up_votes += 1
        flash("Thanks for your vote!", "success")
    elif vote_type == 'down':
        idea.down_votes += 1
        flash("Thanks for your vote!", "success")
    else:
        flash("Invalid vote type.", "error")
    db.session.commit()
    return redirect(url_for('ideas'))

if __name__ == '__main__':
    # Create the database tables if they don't exist
    with app.app_context():
        db.create_all()
    app.run(debug=True,port=5005)