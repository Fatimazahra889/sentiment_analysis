Overview
This project integrates sentiment analysis with an ESP32 to classify and visualize emotions based on text input. Using machine learning, an SVM model trained on the Sentiment140 dataset processes text to determine sentiment (positive, negative, or neutral). The result is then sent to the ESP32 via MQTT, where it is displayed on an ILI9341 screen along with audio feedback.

🔗 Live Simulation in Wokwi: [Click here to view](https://wokwi.com/projects/423397511758760961)

Features
* Sentiment classification using Support Vector Machine (SVM)
* Real-time MQTT communication between the model and ESP32
* Display sentiment as facial expressions on an ILI9341 screen
* Audio feedback indicating positive or negative sentiment
* Fully simulated in Wokwi, making it hardware-free

 Tech Stack & Skills Used
🔹 Machine Learning: Support Vector Machine (SVM), Sentiment140 dataset
🔹 Embedded Systems: ESP32, ILI9341 screen
🔹 IoT & Communication: MQTT protocol
🔹 Web & API: Flask (for processing sentiment analysis requests)
🔹 Simulation: Wokwi (ESP32 online simulator)

How It Works
1️) A text input is sent to the Flask-based sentiment analysis model
2️) The model classifies it as positive, negative, or neutral
3️) The result is transmitted via MQTT to the ESP32
4️) The ESP32 displays a happy, sad, or neutral face on the ILI9341 screen
5️) An audio message announces whether the sentiment is positive or negative

Future Enhancements
* Improve accuracy by experimenting with deep learning models
* Add more expressive facial animations
* Expand the system for real-time tweet monitoring
