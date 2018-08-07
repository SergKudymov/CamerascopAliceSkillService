"""
Routes and views for the MacroscopAliceSkillService.
"""
import json

from MacroscopAliceSkillService import app
from flask import request

from MacroscopAliceSkillService.request_handler import handle_request


@app.route('/', methods=['POST'])
def main():
    """Get request body and return response"""
    response = handle_request(request.get_json())

    return json.dumps(response, ensure_ascii=False, indent=2)
