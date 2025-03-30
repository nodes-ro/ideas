from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_idea', methods=['GET', 'POST'])
def submit_idea():
    if request.method == 'POST':
        # Handle form data here
        pass
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True,port=5005)