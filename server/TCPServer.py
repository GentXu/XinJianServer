import json
import socket
import threading
from data.MySQL import *

import yaml

"""
认证类服务器
"""


class TCPServer:
    def __init__(self, mysql: MySQL):
        self.tcp_client_map = {}
        self.mysql = mysql
        with open("resource/serverconfig.yml") as yml:
            server_config = yaml.safe_load(yml)
            self.server_ip = server_config["ip"]
            self.server_port = server_config["port"]
        self.tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server.bind((self.server_ip, self.server_port))
        self.tcp_server.listen(100)
        threading.Thread(target=self.tcp_accept).start()
        print("TCP服务开启成功")

    """接收客户端链接请求"""

    def tcp_accept(self):
        while True:
            client_tcp_socket, tcp_address = self.tcp_server.accept()
            tcp_client_ip = tcp_address[0] + ":" + str(tcp_address[1])
            print(tcp_client_ip, "用户已连接")
            self.tcp_client_map[tcp_client_ip] = client_tcp_socket
            threading.Thread(target=self.tcp_recv_msg, args=(client_tcp_socket, tcp_client_ip)).start()

    """
    客户端链接后处理客户端发送的消息
    """

    def tcp_recv_msg(self, channel, client_ip):
        while True:
            try:
                data = channel.recv(1024).decode('utf-8')
                """
                客户端断开链接时会持续发送空消息
                断开客户端链接
                """
                if not data:
                    self.tcp_client_map.pop(client_ip)
                    break
                # 获得字典数据
                dict_data = json.loads(data)
                dict_data["ip"] = client_ip
                match dict_data:
                    case {"interface": "soft"}:
                        self.soft_method(dict_data, channel)
                # channel.send(data.encode('utf-8'))
            except ConnectionResetError:
                self.tcp_client_map.pop(client_ip)
                break

    """处理面向软件接口的请求"""
    def soft_method(self, dict_data, channel):
        sql_result = None
        match dict_data:
            case {"method": "register"}:
                sql_result = json.dumps({
                    "msg": self.mysql.register(dict_data)
                })
            case {"method": "login"}:
                sql_result = json.dumps({
                    "msg": self.mysql.login(dict_data)
                })
            case {"method": "get_user_info"}:
                sql_tuple = self.mysql.get_user_info(dict_data)
                sql_result = json.dumps({
                    "id": sql_tuple[0],
                    "user": sql_tuple[1],
                    "name": sql_tuple[2],
                    "xb": sql_tuple[4],
                    "birthday": sql_tuple[5],
                    "motto": sql_tuple[6],
                    "ip": sql_tuple[7]
                })
        channel.send(sql_result.encode('utf-8'))
