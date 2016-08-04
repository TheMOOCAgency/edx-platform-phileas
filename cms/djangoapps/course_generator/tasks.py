"""
Asynchronous tasks for the course generator app.
"""
import json

from celery.task.schedules import crontab
from celery.decorators import periodic_task

from django.conf import settings

from course_generator.helpers import create_course


@periodic_task(
    run_every=(crontab(minute=0, hour=0)),
    name="course_generator.course_json_consumer",
    ignore_result=True
)
def course_json_consumer():
    """
    Reads the JSON, processed and creates courses if not already created.
    """
    # Read the JSON
    file_path = settings.COURSE_JSON_LOCATION / settings.COURSE_JSON_FILE_NAME
    json_data = None
    with open(file_path) as data_file:
        json_data = json.load(data_file)

    # If JSON data available then get course details
    if json_data:
        formations = json_data.get('data', {}).get('formations', [])
        for formation in formations:
            create_course(formation)