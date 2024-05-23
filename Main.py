import json
import socket
import threading
from data.MySQL import *

tcp_client_map = {}
udp_client_map = {}


"""
UDP发送消息
"""


def send_msg(msg, ip):
    print(ip, ",", msg)
    split = msg.split("@")
    if len(split) != 2:
        udp_server.sendto("格式错误！".encode('gbk'), ip)
    else:
        if "initialize" in msg:
            send = "Server1@" + ip[0] + ":" + str(ip[1])
            udp_server.sendto(send.encode('gbk'), ip)
            return
        if split[0] in udp_client_map:
            target = udp_client_map.get(split[0])
            udp_server.sendto(split[1].encode('gbk'), target)
        else:
            udp_server.sendto("用户没上线！".encode('gbk'), ip)


"""
多线程接受客户端消息
"""


def tcp_recv_msg(channel, client_ip):
    while True:
        try:
            data = channel.recv(1024).decode('utf-8')
            # 获得字典数据
            dict_data = json.loads(data)
            dict_data["ip"] = client_ip
            interface = dict_data["interface"]
            if "soft" in interface:
                soft_method(dict_data, interface, channel)
            # channel.send(data.encode('utf-8'))
        except ConnectionResetError:
            tcp_client_map.pop(client_ip)
            break
        if not data:
            tcp_client_map.pop(client_ip)
            break


"""
软件接口处理
"""


def soft_method(dict_data, interface, channel):
    if "register" in interface:
        sql_result = json.dumps({
            "msg": mysql.register(dict_data)
        })
        channel.send(sql_result.encode('utf-8'))
    elif "login" in interface:
        sql_result = json.dumps({
            "msg": mysql.login(dict_data)
        })
        channel.send(sql_result.encode('utf-8'))
    elif "get_user_info" in interface:
        sql_tuple = mysql.get_user_info(dict_data)
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


""" 
单独开一个线程死循环接收客户端连接
并将socket存入map
"""


def tcp_accept():
    while True:
        client_tcp_socket, tcp_address = tcp_server.accept()
        tcp_client_ip = tcp_address[0] + ":" + str(tcp_address[1])
        print(tcp_client_ip, "用户已连接")
        tcp_client_map[tcp_client_ip] = client_tcp_socket
        threading.Thread(target=tcp_recv_msg, args=(client_tcp_socket, tcp_client_ip)).start()


if __name__ == '__main__':
    host = socket.gethostname()
    ip_address = socket.gethostbyname(host)
    tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server.bind((ip_address, 15061))
    tcp_server.listen(100)
    threading.Thread(target=tcp_accept).start()
    print("TCP服务器启动成功")
    udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_server.bind((ip_address, 15061))
    print("UDP服务器启动成功")
    try:
        mysql = MySQL()
        cursor = mysql.connect()
        cursor.execute('select version()')
        result = cursor.fetchall()
        print("数据库连接成功")
    except Exception as e:
        print("数据库连接失败")
    while True:
        message, ip = udp_server.recvfrom(1024)
        key = ip[0] + ":" + str(ip[1])
        udp_client_map[key] = ip
        msg_mod = message.decode('gbk')
        threading.Thread(target=send_msg, args=(msg_mod, ip)).start()