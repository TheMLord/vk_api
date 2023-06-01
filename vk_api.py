"""Модуль с классом VkApi"""
import json
import socket
import ssl
import pandas as pd


def get_token(file_with_key: str):
    """Функция для получения сервисного ключа из файла

    :param file_with_key: путь до файла с сервисным ключом api приложения
    :return: возвращает ключ в виде строки
    """
    with open(file_with_key, "r", encoding="UTF-8") as file_key:
        return file_key.read()


def prepare_message(dict_data: dict):
    """Функция подготовки сообщения к отправке

    :param dict_data: словарь с заготовками для сообщения
    :return: возвращает подготовленное сообщение
    """
    message = dict_data["method"] + " " + dict_data["url"] + f" HTTP/{dict_data['version_http']}\n"
    for header, value in dict_data["headers"].items():
        message += f"{header}: {value}\n"
    message += "\n"

    if dict_data["body"] is not None:
        message += dict_data["body"]

    return message


class VkApi:
    """Класс VkApi

    """

    def __init__(self):
        """Функция инициализации класса

        """
        self.access_token = get_token("service_key.txt")
        self.HOST_ADDR = "api.vk.com"
        self.PORT = 443
        self.answer_table = pd.DataFrame(columns=["ID", "First name", "Last_name"])

    def get_user_friends(self, user_id: str):
        """Функция получения списка друзей пользователя

        :param user_id: id пользователя
        """
        try:
            ssl_contex = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ssl_contex.check_hostname = False
            ssl_contex.verify_mode = ssl.CERT_NONE
            with socket.create_connection((self.HOST_ADDR, self.PORT)) as sock:
                try:
                    with ssl_contex.wrap_socket(sock, server_hostname=self.HOST_ADDR) as client:
                        message = prepare_message(
                            {
                                "method": "GET",
                                "url": f"https://api.vk.com/method/friends.get?user_id={user_id}"
                                       f"&access_token={self.access_token}&fields=nickname&v=5.131",
                                "version_http": "1.1",
                                "headers":
                                    {
                                        "Host": self.HOST_ADDR,
                                        "Accept": "application/json",
                                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                                                      "Chrome/58.0.3029.110 Safari/537.3",
                                        "Authorization": f"Bearer {self.access_token}",
                                        "Content-Type": "application/x-www-form-urlencoded"
                                    },
                                "body": None
                            }
                        )
                        answer_json = self.send_request_api(client, message)
                        if answer_json:
                            print(f"Список друзей пользователя - {user_id}")
                            self.prepare_answer(self.send_request_api(client, message))
                        else:
                            print("неверно указан id пользователя")
                except ssl.SSLError as e:
                    print(f"Ошибка SSL: {e}")
        except socket.error as e:
            print(f"Ошибка сокета: {e}")

    def prepare_answer(self, answer_json: dict):
        """Функция подготовки результата запроса к выводу на консоль

        :param answer_json: словарь с ответом
        """
        counter = 0
        info_friends = answer_json["response"]["items"]
        print(f"количество друзей - {len(info_friends)}")
        for info in info_friends:
            self.answer_table.loc[counter] = [info["id"], info["first_name"], info["last_name"]]
            counter += 1
        print(self.answer_table.to_string(index=False))

    def send_request_api(self, client_socket: socket, prepared_message: str):
        """Функция отправки запроса на сервер

        :param client_socket: сокет
        :param prepared_message: подготовленное к отправке сообщение
        :return: возвращает json с ответом
        """
        client_socket.send((prepared_message + '\n').encode())
        return self.get_response(client_socket)

    def get_response(self, client_socket: socket):
        """Функция для получения ответов от сервера

        :param client_socket: cокет
        :return: возвращает ответ от сервера
        """
        client_socket.settimeout(1)
        recv_data = ""
        while True:
            try:
                recv_data += client_socket.recv(1024).decode("UTF-8")
            except socket.timeout:
                try:
                    answer = json.loads(recv_data[recv_data.find("{"):])
                    return answer
                except Exception:
                    return {}
