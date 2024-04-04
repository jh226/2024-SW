import sys
from PyQt5.QtWidgets import QApplication
import pymysql

class mysqlDB():
    def __init__(self) -> None:
        pymysql.version_info=(1,4,2,"final",0)
        pymysql.install_as_MySQLdb()
        super().__init__()
        self.connection = pymysql.connect(
            host='localhost',
            user='root',
            passwd='1234',
            db='sa',
            charset='utf8',
            port=3306,
            cursorclass=pymysql.cursors.DictCursor
        )

    def disconnect(self):
        if self.connection.ping():
            self.connection.close()
            print("MySQL 서버 연결이 종료되었습니다.")
        else:
            print("연결되지 않은 상태입니다.")
            
    def insert(self, new_name, new_phone, new_pic):
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO addbook (name, phone, filename) VALUES (%s, %s, %s)"
            result = cursor.execute(sql, (new_name, new_phone, new_pic))
            self.connection.commit()
            
            print(result, "개 행 실행 완료")
            return result
        
    def update(self, name_key, new_phone, new_pic):
        with self.connection.cursor() as cursor:
            sql = "UPDATE addbook SET phone=%s, filename=%s WHERE name=%s"
            result = cursor.execute(sql, (new_phone, new_pic, name_key))
            self.connection.commit()
            
            print(result, "개 행 실행 완료")
            return result
    
    def delete(self, name_key,phone_key):
        with self.connection.cursor() as cursor:
            sql = "DELETE FROM addbook WHERE name=%s And phone=%s"
            result = cursor.execute(sql, (name_key, phone_key))
            self.connection.commit()
            
            print(result, "개 행 실행 완료")
            return result
        
    def select(self, name_key,phone_key):
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM addbook WHERE name=%s And phone=%s"
            result = cursor.execute(sql, (name_key, phone_key))
            result = cursor.fetchall()
            
            print(result)
            return result

    def select_all(self):
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM addbook WHERE 1"
            result = cursor.execute(sql)
            result = cursor.fetchall()
            
            print(result)
            return result

if __name__ == '__main__':
    app = QApplication(sys.argv)
    db = mysqlDB()
    
    # result = db.insert("이길동", "010-3333-3333", "")
    # result = db.update("이길동", "010-2222-2222", "")
    # result = db.delete("이길동", "010-2222-2222")
    # result = db.select("이길동", "010-2222-2222")