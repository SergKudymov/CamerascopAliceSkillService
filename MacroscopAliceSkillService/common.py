suggests_buttons = [
    {'title': 'Demo сервер', 'hide': False},
    {'title': 'Зайти на свой сервер', 'hide': False},
    {'title': 'Что такое Камераскоп?', 'hide': False}
]


def get_response_pattern(request):
    response_pattern = {
        "version": request['version'],
        "session": request['session'],
        "response": {
            "end_session": False
        }
    }
    return response_pattern