import pymysql
from utils.AESUtil import *


class MySQL:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.soft = None

    """
    连接数据库并返回一个游标
    """

    def connect(self):
        conn = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='root',
            database='xinjian'
        )
        self.conn = conn

        self.cursor = conn.cursor()
        self.soft = self.Soft(self.conn, self.cursor)
        return conn.cursor()

    def register(self, data):
        return self.soft.register(data)

    def login(self, data):
        return self.soft.login(data)

    def get_user_info(self, data):
        return self.soft.get_user_info(data)

    """
    软件接口
    """

    class Soft:
        def __init__(self, conn, cursor):
            self.cursor = cursor
            self.conn = conn

        """用户注册"""
        def register(self, data):
            sql = ("INSERT INTO `user` (`id`, `user`, `name`, `passwd`, `xb`, `birthday`, `motto`, `IP`)"
                   " VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)")
            try:
                passwd = data["passwd"]
                en_passwd = encrypt(passwd, "ndxshishuaibi666")
                self.cursor.execute(sql, (data["user"], data["name"], en_passwd, data["xb"],
                                          data["birthday"], data["motto"], data["ip"]))
                self.conn.commit()
                print("完成一条来自 " + data["ip"] + " 的注册请求")
                return True
            except Exception as ex:
                self.conn.rollback()
                print(ex)
                return False

        """用户登录"""
        def login(self, data):
            sql = "SELECT `passwd` from user where user=%s"
            update_ip = "UPDATE `user` SET `IP` = %s WHERE `user`.`id` = %s"
            try:
                self.cursor.execute(sql, (data["user"]))
                result = self.cursor.fetchone()
                passwd = data["passwd"]
                de_passwd = decrypt(result[0], "ndxshishuaibi666")
                if passwd == de_passwd:
                    # 用户登录时更新IP地址
                    try:
                        user_id = self.get_user_info(data)[0]
                        self.cursor.execute(update_ip, (data["ip"], user_id))
                        self.conn.commit()
                    except Exception as ex:
                        self.conn.fallback()
                        print("在更新用户IP时出现问题:")
                        print(ex)
                    return True
                else:
                    return False
            except Exception as ex:
                print(ex)
                return False

        """获得用户数据"""
        def get_user_info(self, data):
            sql = "SELECT * from user where user=%s"
            try:
                self.cursor.execute(sql, (data["user"]))
                result = self.cursor.fetchone()
                print(result)
                return result
            except Exception as ex:
                print(ex)


if __name__ == '__main__':
    mysql = MySQL()
    mysql_cursor = mysql.connect()
    user_data = {
        "id": 1
    }
    mysql.get_user_info(user_data)
