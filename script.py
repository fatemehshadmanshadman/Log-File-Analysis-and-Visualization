import mysql.connector
from mysql.connector import Error
import matplotlib.pyplot as mat

vars=[]

def read():    
    with open("script/nginx_logs.txt",mode='r') as ng:
        lines=ng.readlines()
        for line in lines:
            var=line.split(" ")
            vars.append(var)
    print("read logs")
    
def store():
    connection=None
    cursor=None
    
    try:
        connection=mysql.connector.connect(
            host="localhost",
            user="admin",
            password="1234"
        )      
        cursor=connection.cursor()

        #create database
        cursor.execute("show databases")
        dbs=cursor.fetchall()
        if ('nginx',) in dbs:
            print("database exist")
        else:
            cursor.execute(f"create database nginx")
            print("database created")
        
        #craete table
        connection.database="nginx"
        cursor.execute("show tables")
        tbs=cursor.fetchall()
        if ('logs',) in tbs:
            print("table exist")
        else:
            cursor.execute("""create table logs(
                id INT AUTO_INCREMENT PRIMARY KEY, 
                ip VARCHAR(20),
                datee VARCHAR(50),
                method VARCHAR(10), 
                address NVARCHAR(100),
                status INT,
                size INT)""")    
            print("table created")
        
        print("wait a minute logs insert into the table you can stop by CTRL+C")
        #insert into table  
        count=0  
        cursor.execute("select id from logs order by id desc limit 1")
        last_id= cursor.fetchone()
        if last_id == None:
            last_id=0
        else:
            last_id=last_id[0]

        for var in vars[last_id:]:  
            if '-' in var[9]:
                var[9]=0
            else:
                var[9]=int(str(var[9]).strip())
                         
            sql="INSERT INTO logs(ip,datee,method,address,status,size)VALUES(%s,%s,%s,%s,%s,%s)"   #%s,%s,%s,%s,%s,%s(?,?,?,?,?,?)            
            value=(var[0],var[3][1:],var[5][1:],var[6],var[8],var[9])
            cursor.execute(sql,value)
            connection.commit()
            count+=1
            # print("insert")
            
        print(f"insert {count} logs")
        
        
    except Error:
        print(f"there is error: {Error}")
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def generate(status_code=[200,404],status_title=["success","error"]):
    result=[]
    try:
        connection=mysql.connector.connect(
            host="localhost",
            user="admin",
            password="1234",
            database="nginx"
        )
        cursor=connection.cursor()
        
        for i in status_code:
            sql="select * from logs where status=%s"
            cursor.execute(sql,(i,))
            result.append(cursor.fetchall())            
        count=[len(i) for i in result]
        
        mat.figure(figsize=(8,8))
        mat.title("Server Status Bar Chart")
        mat.xlabel("Status Title")
        mat.ylabel("Status Count")
        mat.bar(status_title,count,width=0.2,color='pink')
        mat.grid()        
        mat.show()
    
    except Error:
        print(f"{Error} in generating")
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

read()
i=int(input("1.Store the Data \n2.Visualizations\n"))
if i==1:     
    store()
elif i==2:
    generate([200,404,301,302,500],["Success","Error","Move","Edit"," Server Error"])