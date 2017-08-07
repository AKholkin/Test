import sqlite3
import random
import requests
import json
import time
import os
import sys
from string import ascii_letters
import logging

logging.basicConfig(level=logging.DEBUG)

# step 1

logging.info("Step 1")
sudo_pass = sys.argv[0]
tmp = (os.popen("echo {password} | sudo -S  find /var/lib/docker/aufs/diff/"
                " -name clients.db".format(password=sudo_pass)).read())

os.popen("echo {password} | sudo -S cp {db_file} /tmp".format(
    db_file=tmp.split()[2], password=sudo_pass))
sqlite_file = '/tmp/clients.db'
conn = sqlite3.connect(sqlite_file)

# step 2

logging.info("Step 2")
c = conn.cursor()
c.execute("SELECT CLIENT_ID, BALANCE FROM CLIENTS, BALANCES "
          "WHERE (BALANCE > 0) AND (CLIENT_ID = CLIENTS_CLIENT_ID)")

info = c.fetchall()
if not info:
    c.execute("SELECT CLIENT_ID FROM CLIENTS")
    ids = c.fetchall()
    unique_id = ids
    while True:
        unique_id = random.randint(0, 10000)
        if unique_id not in ids:
            break
    client_name = ''.join(random.choice(ascii_letters) for i in range(12))
    c.executemany("INSERT INTO CLIENTS(CLIENT_ID, CLIENT_NAME) VALUES(?, ?)",
                  [(unique_id, client_name)])
    c.executemany("INSERT INTO BALANCES(CLIENTS_CLIENT_ID, BALANCE)"
                  " VALUES(?, ?)", [(unique_id, 5.0)])
    conn.commit()

    c.execute("SELECT CLIENT_ID, BALANCE FROM CLIENTS, BALANCES "
              "WHERE CLIENT_ID = CLIENTS_CLIENT_ID")
    info = c.fetchall()

client = random.choice(info)
logging.info("client id and balance")
logging.info(client)

c.close()
conn.close()
os.popen("echo {password} | sudo -S rm /tmp/clients.db".format(password=sudo_pass))

# step 3


def post_client_services(data, url):
    headers = {"Content-type": "application/json", "Accept": "text/plain"}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    return r

logging.info("Step 3")
data = {"client_id": client[0]}
url = "http://localhost:5000/client/services"
answer = post_client_services(data, url)

service_list = json.loads(answer.text)
clients_services = []
for i in service_list["items"]:
    clients_services.append(i["name"])
logging.info("clients_services")
logging.info(clients_services)

# step 4
logging.info("Step 4")
headers = {"Content-type": "application/json", "Accept": "text/plain"}
r = requests.get("http://localhost:5000/services")
service_list = json.loads(r.text)
all_services = []
for i in service_list["items"]:
    all_services.append(i["name"])
logging.info("all_services")
logging.info(all_services)

# step 5

logging.info("Step 5")
unconnected_services = list(set(all_services) - set(clients_services))
service = 0
try:
    service = random.choice(unconnected_services)
except Exception.message:
    logging.error("No_unconnected_services")
    exit()

headers = {"Content-type": "application/json", "Accept": "text/plain"}
r = requests.get("http://localhost:5000/services")
service_id_and_cost = []
service_list = json.loads(r.text)
for i in service_list["items"]:
    if i["name"] == service:
        service_id_and_cost.append((i["id"], i["cost"]))
    all_services.append(i["name"])
logging.info("service_id_and_cost")
logging.info(service_id_and_cost)

# step 6

logging.info("Step 6")
data = {"client_id": client[0], "service_id": service_id_and_cost[0][0]}
url = "http://localhost:5000/client/add_service"
answer = post_client_services(data, url)
if answer.status_code != 202:
    logging.error("adding service error")
    exit()
logging.info("answer.status_code")
logging.info(answer.status_code)

# step 7

logging.info("Step 7")
time_start = time.time()
time_sleep = time_start - time.time()
adding_service = False

while time_sleep > - 60:
    data = {"client_id": client[0]}
    url = "http://localhost:5000/client/services"
    answ = post_client_services(data, url)
    service_list_new = json.loads(answ.text)

    for i in service_list_new["items"]:
        if i["id"] == service_id_and_cost[0][0]:
            adding_service = True

    if adding_service:
        logging.info("service was added")
        break
    time.sleep(10)
    time_sleep = time_start - time.time()

if not adding_service:
    logging.error("adding is out of time")
    exit()

tmp = (os.popen("echo {password} | sudo -S  find /var/lib/docker/aufs/diff/"
                " -name clients.db".format(password=sudo_pass)).read())

os.popen("echo {password} | sudo -S cp {db_file} /tmp".format(
    db_file=tmp.split()[2], password=sudo_pass))
sqlite_file = '/tmp/clients.db'

conn = sqlite3.connect(sqlite_file)
c = conn.cursor()

# step 8

logging.info("Step 8")
select = "SELECT BALANCE FROM BALANCES WHERE CLIENTS_CLIENT_ID = {s}".format(s=client[0])
c.execute(select)
info = c.fetchall()[0][0]

# step 9

logging.info("Step 9")
if info == client[1] - service_id_and_cost[0][1]:
    logging.info("Pass")
    print "Test passed"
else:
    print "Balances are not equal"

os.popen("echo {password} | sudo -S rm /tmp/clients.db".format(password=sudo_pass))
c.close()
conn.close()

