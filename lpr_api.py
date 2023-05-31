from fastapi import FastAPI
import uvicorn
import mysql.connector
db = mysql.connector.connect(host="localhost",username="root",password = '',database='license_plate_rec')
db_cur = db.cursor()
def search_plate(plate2search):
    global db_cur
    sql_search = ("SELECT data_user.user_name,data_user.house_num,data_car.car_id,data_car.car_license_str FROM data_car JOIN data_user ON data_car.user_id = data_user.user_id WHERE car_license_str = %s")
    print("search:",plate2search)
    db_cur.execute(sql_search,[plate2search])
    result = db_cur.fetchall()  
    return result
def gate_log(car_id,action):
    global db_cur,db
    add_log=("INSERT INTO `gate_log`(`car_id`, `gate_action`, `gate_time_stamp`) VALUES (%s,%s,CURRENT_TIMESTAMP)")
    log_data = [car_id,action]
    db_cur.execute(add_log,log_data)
    db.commit()

app = FastAPI()

plate_found = False
@app.get("/")
def read_root():
    return {"Nothing: page"}

@app.get("/plate_check/{text}")
def read_plate(text: str):
    global plate_found
    print(text)
    sql_search = ("SELECT data_user.user_name,data_user.house_num,data_car.car_id,data_car.car_license_str FROM data_car JOIN data_user ON data_car.user_id = data_user.user_id WHERE car_license_str = %s")
    db_cur.execute(sql_search,[text])
    result = db_cur.fetchall() 
    if (len(result) != 0):
        add_log=("INSERT INTO `gate_log`(`car_id`, `gate_action`, `gate_time_stamp`) VALUES (%s,%s,CURRENT_TIMESTAMP)")
        log_data = [result[0][2],"enter/exit"]
        db_cur.execute(add_log,log_data)
        db.commit()
        return True
    else:
        return False
if __name__ == "__main__":
    uvicorn.run("lpr_api:app", host="0.0.0.0", port=5050, log_level="info")
    # uvicorn lpr_api:app --host 0.0.0.0 --port 5050