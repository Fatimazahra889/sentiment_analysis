from flask import Flask, render_template, request
import joblib
import sqlite3
from io import BytesIO
import base64
from datetime import datetime
import matplotlib.dates as mdates
import paho.mqtt.client as mqtt

import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend
import matplotlib.pyplot as plt

app = Flask(__name__)
app.secret_key = "secret_key"

# MQTT Configuration
MQTT_BROKER = "broker.hivemq.com"  # Use HiveMQ
MQTT_PORT = 1883  # Default MQTT port
MQTT_TOPIC = "flaskapp"  # ✅ Only one topic now

# MQTT Client Setup
mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)  
mqtt_client.loop_start()  # Start MQTT loop in the background

# Load the model and vectorizer
model = joblib.load('model/svm_model.pkl')
vectorizer = joblib.load('model/vectorizer.pkl')

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS sentiments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        text TEXT,
                        prediction TEXT,
                        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html')

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        text = request.form['text']
        text_vec = vectorizer.transform([text])
        prediction = model.predict(text_vec)

        if prediction[0] == 'Positive':
            sentiment = "Positive"
            img_tag = "<img src='/static/images/happy.png' alt='Positive' width='40' height='40'>"
        elif prediction[0] == 'Negative':
            sentiment = "Negative"
            img_tag = "<img src='/static/images/angry.png' alt='Negative' width='40' height='40'>"
        else:
            sentiment = "Neutral"
            img_tag = "<img src='/static/images/neutral.png' alt='Neutral' width='40' height='40'>"

        # Save to database
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sentiments (text, prediction) VALUES (?, ?)", (text, prediction[0]))
        conn.commit()
        conn.close()

        # ✅ Publish sentiment to MQTT topic
        mqtt_client.publish(MQTT_TOPIC, sentiment)

        return render_template('how_it_works.html', prediction_text=f"{text} : {sentiment} {img_tag}")

def create_graph(dates_str, y, title, color):
    dates = [datetime.strptime(d, '%Y-%m-%d %H:%M:%S') for d in dates_str]
    fig, ax = plt.subplots()
    ax.plot(dates, y, marker='o', linestyle='-', color=color)
    ax.set_title(title)
    ax.set_xlabel("Temps")
    ax.set_ylabel("Nombre de Messages")
    
    # Format dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    img = BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plt.close(fig)  
    return base64.b64encode(img.getvalue()).decode('utf-8')

@app.route('/stats')
def stats():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT date, prediction FROM sentiments WHERE date >= datetime('now', '-24 hours') ORDER BY date;")
    sentiment_data = cursor.fetchall()
    conn.close()

    if not sentiment_data:
        return render_template('stats.html', message="Aucun message enregistré.")

    dates, positives, neutrals, negatives = [], [], [], []
    pos_count = neu_count = neg_count = 0

    for date, sentiment in sentiment_data:
        dates.append(date)
        if sentiment == 'Positive':
            pos_count += 1
        elif sentiment == 'Neutral':
            neu_count += 1
        elif sentiment == 'Negative':
            neg_count += 1
        positives.append(pos_count)
        neutrals.append(neu_count)
        negatives.append(neg_count)
    
    img_pos = create_graph(dates, positives, "Évolution des Positifs", "green")
    img_neu = create_graph(dates, neutrals, "Évolution des Neutres", "yellow")
    img_neg = create_graph(dates, negatives, "Évolution des Négatifs", "red")
    
    return render_template('stats.html', img_pos=img_pos, img_neu=img_neu, img_neg=img_neg)

if __name__ == "__main__":
    app.run(debug=True, port=8080)  




