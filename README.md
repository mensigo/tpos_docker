*Docker-compose project*

Services:
- db (mysql)
- csv_load (python)
- app (flask)


To verify that data is loaded:
cd csv_load/check && pip3 install -r requirements.txt && python3 check.py


To verify GET:
- curl http://0.0.0.0:23069/
- curl http://0.0.0.0:23069/health
- curl http://0.0.0.0:23069/something


Details:
- by default, the first row of .csv file is ignored, but it can be managed via main(...) param in csv_load/load_csv.py
- service #1 (db): data is not hard-coded, but loaded via service #2 (only empty database is initialized with db/init.sql)
- service #2 (csv_load): data verification with csv_load/check/check.py, volumed .csv file (in .yml),
container stops (no need to remove), data .csv is not hard-coded
- service #3 (app): GET / returns .json (data), GET /health returns 200 (status), other requests return custom message
