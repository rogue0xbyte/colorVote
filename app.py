from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.json_util import dumps
from flask_cors import CORS
from pymongo.server_api import ServerApi

app = Flask(__name__)
CORS(app)

client = MongoClient(
    'mongodb+srv://theeye:test@eyecommunity.48uzc.mongodb.net/?retryWrites=true&w=majority&appName=eyeCommunity', 
    server_api=ServerApi('1')
)
db = client['eyeCommunity']
collection = db['colorpollresponses']

def calculate_average_color():
    votes = list(collection.find())
    if not votes:
        return (255, 255, 255)  # Default to white if no votes
    total_r = total_g = total_b = 0
    for vote in votes:
        r, g, b = vote['color']
        total_r += r
        total_g += g
        total_b += b
    count = len(votes)
    return (total_r // count, total_g // count, total_b // count)
@app.route('/', methods=['GET', 'POST'])
def red():
    return redirect(url_for('vote'))

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if request.method == 'POST':
        color = request.form.get('color')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
        collection.insert_one({'color': (r, g, b)})
        return redirect(url_for('view'))
    avg_color = calculate_average_color()
    avg_hex = '#{:02x}{:02x}{:02x}'.format(*avg_color)
    return render_template('vote.html', avg_color=avg_hex)

@app.route('/view')
def view():
    avg_color = calculate_average_color()
    avg_hex = '#{:02x}{:02x}{:02x}'.format(*avg_color)
    return render_template('view.html', avg_color=avg_hex, rgb=avg_color)

# @app.route('/clear')
# def clear():
#     collection.delete_many({})  # Clears all documents in the collection
#     return "All votes have been cleared!", 200

if __name__ == '__main__':
    app.run(debug=True)
