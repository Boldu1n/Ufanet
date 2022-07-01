import pymysql

def my_request(sql):
	con = pymysql.connect(host='localhost',user='user',password='user',database='rooms',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
	cursor = con.cursor()
	cursor.execute(sql)
	if sql.find("INSERT")!=-1:
		con.commit()
	else:
		rows = cursor.fetchall()
		return rows
	cursor.close()
	con.close()
