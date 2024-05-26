from server.TCPServer import *
from server.UDPServer import *

if __name__ == '__main__':
    try:
        mysql = MySQL()
        cursor = mysql.connect()
        cursor.execute('select version()')
        result = cursor.fetchall()
        print("数据库连接成功")
        tcp_server = TCPServer(mysql)
        udp_server = UDPServer(mysql)
    except Exception as e:
        print("数据库连接失败")
        print(e)
    while True:
        pass
