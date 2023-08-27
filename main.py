import json
import os
import requests
import threading
from datetime import datetime
from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_caching import Cache
import schedule
import logging

app = Flask(__name__, static_folder='static')
app.config['CACHE_TYPE'] = 'simple'
cache = Cache(app)
app.logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
app.logger.addHandler(handler)

# Constants
CONFIG = {
    'JSON_URL': "https://raw.githubusercontent.com/swaggyP36000/TrollStore-IPAs/main/apps.json",
    'JSON_FILENAME': "apps.json",
}


class AppForm(FlaskForm):
    app_name = StringField('App Name', validators=[DataRequired()])
    version = StringField('Version', validators=[DataRequired()])
    submit = SubmitField('Add App')

# Utility functions


def get_remote_mod_time(url):
    try:
        response = requests.head(url)
        response.raise_for_status()
        return datetime.strptime(response.headers.get("Last-Modified", ""), "%a, %d %b %Y %H:%M:%S %Z") if "Last-Modified" in response.headers else None
    except requests.exceptions.RequestException as exc:
        app.logger.error(f"Error getting remote modification time: {exc}")
        return None


def download_and_save_json(url, filename):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(filename, "w") as json_file:
            json.dump(response.json(), json_file, indent=4)
        app.logger.info(f"JSON data downloaded and saved as '{filename}'.")
    except (requests.RequestException, json.JSONDecodeError) as exc:
        app.logger.error(f"An error occurred while downloading JSON: {exc}")


def load_json(file_path):
    try:
        with open(file_path, 'r') as json_file:
            return json.load(json_file)
    except (IOError, json.JSONDecodeError) as exc:
        app.logger.error(f"Error loading JSON: {exc}")
        return None


def update_files():
    app.logger.info("Updating JSON file...")

    try:
        if os.path.exists(CONFIG['JSON_FILENAME']):
            local_mod_time = datetime.fromtimestamp(
                os.path.getmtime(CONFIG['JSON_FILENAME']))
            remote_mod_time = get_remote_mod_time(CONFIG['JSON_URL'])
            if remote_mod_time and remote_mod_time > local_mod_time:
                app.logger.info(
                    f"'{CONFIG['JSON_FILENAME']}' is outdated. Downloading the updated JSON.")
                download_and_save_json(
                    CONFIG['JSON_URL'], CONFIG['JSON_FILENAME'])
            else:
                app.logger.info(
                    f"'{CONFIG['JSON_FILENAME']}' is up to date. No need to download.")
        else:
            download_and_save_json(CONFIG['JSON_URL'], CONFIG['JSON_FILENAME'])
    except Exception as exc:
        app.logger.error(f"An error occurred: {exc}")

# Flask routes


@app.route('/')
@cache.cached(timeout=3600)  # Cache for 1 hour
def index():
    app_versions = {}
    app_names = []

    try:
        json_data = load_json(CONFIG['JSON_FILENAME'])
        if json_data:
            apps_list = json_data['apps']
            app_names = [app['name']
                         for app in apps_list]  # Populate app_names list
            for app in apps_list:
                app_name = app['name']
                app_version = app['version']
                if app_name not in app_versions:
                    app_versions[app_name] = []
                app_versions[app_name].append({
                    'version': app_version,
                    'download_url': app['downloadURL'],
                    'icon_url': app['iconURL'],
                    'size': app['size']
                })
    except IOError as exc:
        app.logger.error(f"Error reading JSON file: {exc}")

    return render_template('main.html', app_versions=app_versions, app_names=app_names)
# Main function


def main():
    download_and_save_json(CONFIG['JSON_URL'], CONFIG['JSON_FILENAME'])
    update_files()

    schedule.every(1).hour.do(update_files)
    update_thread = threading.Thread(target=update_files)
    update_thread.start()

    app.run(host='0.0.0.0', port=8080, debug=True)


if __name__ == "__main__":
    main()
