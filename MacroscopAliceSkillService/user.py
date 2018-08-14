from urllib.request import urlopen
from xml.dom import minidom

from MacroscopAliceSkillService.common import get_response_pattern, suggests_buttons


class User:

    def __init__(self, user_id, original_utterance):
        self.user_id = user_id
        self.original_utterance = original_utterance
        self.is_new = True

        self.channels = {}
        self.url = None
        self.login = None
        self.password = None
        self.is_connected_to_server = False

    def login_to_server(self, request):
        response = get_response_pattern(request)
        try:
            spited_request = self.original_utterance.lower().split('%', 3)

            self.url = spited_request[0]
            self.login = spited_request[1]
            self.password = spited_request[2]
        except IndexError:
            response['response']['text'] = 'Вы ввели неправильно, вот шаблон:\n' \
                                           '(ip адрес или доменное имя):(порт)%(логин)%(пароль)'
            response['response']['buttons'] = suggests_buttons
            self.is_connected_to_server = False
            return response

        try:
            output = urlopen(f"http://{self.url}/configex?login={self.login}&password={self.password}").read()
            response = output.decode('utf-8')
        except:
            response['response']['text'] = 'Ошибка аутентификации'
            response['response']['buttons'] = suggests_buttons
            self.is_connected_to_server = False
            return response

        if 'Configuration' in response:
            login_success_response = self.create_start_response(response, request)
            self.is_connected_to_server = True
            return login_success_response
        else:
            response['response']['text'] = 'Неверное имя пользователя или пароль.'
            response['response']['buttons'] = suggests_buttons
            self.is_connected_to_server = False
            return response

    def create_start_response(self, config, request):
        xml_doc = minidom.parseString(config)
        channels = xml_doc.getElementsByTagName('ChannelInfo')
        response = get_response_pattern(request)
        response['response']['text'] = 'Доступные функции:\n' \
                                       '* Генерация тревоги:\n' \
                                       '        Просто скажи: тревога {название камеры в Макроскопе} ' \
                                       '{опциональное сообщение}\n' \
                                       '* Посмотреть видео с камеры:'
        cameras_buttons = []

        for channel in channels:
            channel_id = channel.attributes['Id'].value
            self.channels[channel_id] = channel.attributes['Name'].value
            cameras_buttons.append({'title': channel.attributes['Name'].value,
                                    'url': f'http://{self.url}/mobile?'
                                           f'channelId={channel_id}&'
                                           f'resolutionX=1024&'
                                           f'resolutionY=662&'
                                           f'fps=15&'
                                           f'login={self.login}&'
                                           f'password={self.password}&'
                                           f'is_ajax=true&'
                                           f'whoami=webclient&'
                                           f'withcontenttype=true',
                                    'hide': False})

        response['response']['buttons'] = cameras_buttons

        return response

    def create_alarm(self, request):
        for ch_id, ch_name in self.channels.items():
            ch_name_lower_case = ch_name.lower()
            if ch_name_lower_case in self.original_utterance.lower():
                alarm_message = self.original_utterance.lower().split(ch_name_lower_case, 2)[1]
                mc_server_response = self.execute_alarm(ch_id.encode('utf-8'), alarm_message.encode('utf-8'))
                response = get_response_pattern(request)
                response['response']['text'] = mc_server_response

                return response

    def execute_alarm(self, ch_id, alarm_message):
        output = urlopen(f"http://{self.url}/command?type=generateexternalevent&"
                         f"login={self.login}&"
                         f"password={self.password}&"
                         f"channelid={ch_id}&"
                         f"systemname=AliceService&"
                         f"information={alarm_message}").read()

        mc_server_response = output.decode('utf-8')
        return mc_server_response
