# Sign Language to Speech Web Application

This project uses your webcam to recognize hand gestures in real-time and converts them into spoken words through your browser.

## Features

- **Real-time Gesture Recognition:** Uses MediaPipe to detect hand landmarks from a live webcam feed.
- **Web-Based Interface:** Runs as a local web application using Flask, displaying the video feed directly in your browser.
- **Browser-Based Speech:** Utilizes the browser's built-in Web Speech API to voice the recognized gestures, providing instant audio feedback.

### Recognized Gestures

- **Greetings:** HELLO
- **Basic Needs:** Eat, Water
- **Responses:** YES, NO, Please❌, Okay
- **Social:** Thank You, Call me, I want to talk❌
- **General:** Victory, Awesome, Three, Pointing, Question❌, HELP

## Setup and Usage

Follow these steps to run the application on your local machine.

### 1. Prerequisites

- Python 3.10+
- A webcam

### 2. Installation

Clone the repository or download the source files.

Navigate to the project directory in your terminal and install the required Python packages using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 3. Running the Application

Once the installation is complete, run the following command from the project directory:

```bash
python app.py
```

This will start the Flask web server.

### 4. Accessing the Application

Open your web browser and go to the following address:

[http://127.0.0.1:5000](http://127.0.0.1:5000)

You should see the video from your webcam. Hold up a recognized gesture, and after a moment, you should hear the corresponding word spoken by your browser.

To stop the application, return to your terminal and press `Ctrl+C`.
