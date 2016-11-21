"""
Asynchronous tasks for the course generator app.
"""
import json
from path import path

from celery.task import task
from django.conf import settings

from course_generator.helpers import create_course


@task(name='course_generator.course_json_consumer')
def course_json_consumer():
    """
    Reads the JSON, processed and creates courses if not already created.
    """
    # Read the JSON
    file_path = path(settings.COURSE_JSON_LOCATION) / path(settings.COURSE_JSON_FILE_NAME)
    json_data = None
    with open(file_path) as data_file:
        json_data = json.load(data_file)

    # If JSON data available then get course details
    if json_data:
        subjects = json_data.get('data', {}).get('subject', [])
        for subject in subjects:
            create_course(subject)
