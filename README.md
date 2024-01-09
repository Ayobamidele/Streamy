# Running Streamy as a Flask App

This document provides instructions on how to run a Flask app. It also includes information on creating a virtual environment to isolate the project's dependencies.

## Prerequisites

Before running a Flask app, ensure that you have the following tools installed:

- Python 3
- Pip

## Cloning the Repository

1. Clone the Flask app repository to your local machine using the following command:

```bash
git clone <repository-url>
```

2. Navigate to the cloned repository.

## Creating a Virtual Environment

1. Create a virtual environment for the project using the following command:

```bash
python -m venv venv
```

2. Activate the new virtual environment:

- For Linux/macOS:

```bash
source venv/bin/activate
```

- For Windows:

```bash
venv\Scripts\activate
```

## Installing Dependencies

1. Install the required packages mentioned in the `requirements.txt` file using the following command:

```bash
pip install -r requirements.txt
```

## Running the Flask App

1. Run your Flask app locally using the following command:

```bash
python app.py
```

This will start the Flask server, and you can access your app at `localhost:5000` or `localhost:8000` in your web browser.


Finally to get it all running read this article to set your Spotify ID and secrets that are needed in the app.py -  https://developer.spotify.com/documentation/web-api/concepts/apps.


Once you get them create a .env file and put the ID and secret there making sure to follow the naming conventions as the one described in the app.py for ID and secret.

## Troubleshooting

- If you encounter any issues, make sure that all dependencies are installed and the virtual environment is activated correctly.
  

