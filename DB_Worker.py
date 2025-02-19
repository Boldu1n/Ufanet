from psycopg2 import Error
from connect_db import get_cursor


class DB_Wroker:

    def __init__(self):
        self.db_rooms = 'room'
        self.db_meetings = 'meeting_room'
        self.rooms_count = 0
        self.cursor = get_cursor()

    def execute(self, sql: str = None):
        if sql:
            result = None
            try:
                if not self.cursor:
                    self.cursor = get_cursor()
                self.cursor.execute(sql)
                result = self.cursor.fetchall()
            except (Exception, Error) as error:
                print("Ошибка при работе с PostgreSQL", error)
            finally:
                return result


    def insert(self,insert_data = None):
        sql = f"SELECT * FROM {self.db_meetings} WHERE \"roomNumber\" = " + str(insert_data)
        self.execute(sql)

    def get_room_count(self):
        sql = f"""SELECT COUNT(*) from {self.db_rooms}"""
        self.rooms_count = self.execute(sql)[0][0]
        return self.rooms_count

    def reserve_room(self,data: dict = None):
        sql = "SELECT * FROM room1  WHERE roomnumber={} AND dateres={}".format(str(data['num']),
                                                                               str(data['dateres']).replace("-", ""))
        return self.execute(sql)

    def get_reserved_time(self, roomNumber: int = None, date: str = None, time : str = None):
        sql = f"SELECT * FROM {self.db_meetings} WHERE \"roomNumber\" = " + str(roomNumber)
        return self.execute(sql)

    def check_free_time(self,data: dict = None):
        sql = (f"SELECT COUNT(*) FROM {self.db_meetings} WHERE "
                                                 f"\"roomNumber\" = {str(data['roomNumber'])} "
                                                 f"AND \"datares\" = {str(data['datares'])} "
                                                 f"AND \"timeStart\" <= {str(data['timeStart'])} ")
        return self.execute(sql)


if __name__=="__main__":
    db_worker = DB_Wroker()
    print(db_worker.get_room_count())
    print(db_worker.get_reserved_time(2))

