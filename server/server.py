import sqlite3
from sqlite3 import Connection
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import urllib.parse as urlparse
import json
import base64
from PIL import Image
import io

from class_recognition import do_inference

PATH_JSON = Path(__file__).parent / Path("animals.json")
PATH_DB = Path(__file__).parent / Path("server.db")

def create_db(path: Path):
    conn = sqlite3.connect(path)
    conn.execute(
        """CREATE TABLE animal
         (_id INTEGER PRIMARY KEY AUTOINCREMENT,
         name TEXT NOT NULL,
         description TEXT NOT NULL,
         dangerous BOOLEAN NOT NULL);"""
    )
    conn.execute(
        """CREATE TABLE report
         (_id INTEGER PRIMARY KEY AUTOINCREMENT,
         animal_id INTEGER NOT NULL,
         timestamp INTEGER NOT NULL,
         longitude REAL NOT NULL,
         latitude REAL NOT NULL,
         FOREIGN KEY(animal_id) REFERENCES animal(_id));"""
    )
    conn.execute(
        """CREATE TABLE unique_animal
         (_id INTEGER PRIMARY KEY AUTOINCREMENT,
         animal_id INTEGER NOT NULL,
         FOREIGN KEY(animal_id) REFERENCES animal(_id));"""
    )
    conn.execute(
        """CREATE TABLE match
         (_id INTEGER PRIMARY KEY AUTOINCREMENT,
         unique_animal_id INTEGER NOT NULL,
         report_id INTEGER NOT NULL,
         FOREIGN KEY(unique_animal_id) REFERENCES unique_animal(_id),
         FOREIGN KEY(report_id) REFERENCES report(_id));"""
    )
    with conn:
        add_animals(conn, PATH_JSON)
    return conn

def add_animal(conn: Connection, name: str, description: str, dangerous: bool):
    command = f"INSERT INTO animal (name, description, dangerous)\nVALUES ( '{name}', '{description}', {dangerous} );"  
    conn.execute(command)

def add_animals(conn: Connection, path_json: Path):
    with open(path_json) as f:
        animals = json.load(f)
    for animal in animals:
        add_animal(conn, **animal)

def add_report(conn: Connection, animal_id: int, timestamp: int, longitude: float, latitude: float):         
    command = f"INSERT INTO report (animal_id, timestamp, longitude, latitude)\nVALUES ( {animal_id}, {timestamp}, {longitude}, {latitude} );"  
    conn.execute(command)

def add_unique_animal(conn: Connection, unique_animal_id: int, animal_id: int):         
    command = f"INSERT INTO report (unique_animal_id, animal_id)\nVALUES ( {unique_animal_id}, {animal_id} );"  
    conn.execute(command)

def parse_parameter(parameters: dict, name: str, val_type: type = None):
    value = parameters.get(name, [None])[0]
    if val_type is None:
        return value

    try:
        value = val_type(value)
    except Exception:
        logging.warning(f"Error parsing {name}, value: {value}")
        value = None
    return value
    

class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, conn, *args):
        self.conn = conn
        BaseHTTPRequestHandler.__init__(self, *args)
    
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        if '/add-report' in self.path:
            parameters = urlparse.parse_qs(urlparse.urlparse(self.path).query)
            animal_id = parse_parameter(parameters, "animal_id", int)
            timestamp = parse_parameter(parameters, "timestamp", int)
            longitude = parse_parameter(parameters, "longitude", float)
            latitude = parse_parameter(parameters, "latitude", float)
            params = [animal_id, timestamp, longitude, latitude]
            logging.info(f"params {params}")
            if None in params:
                self.send_error(400)
                return
            with self.conn:
                add_report(self.conn, *params)
        elif '/init-report' in self.path:
            length = int(self.headers.get('content-length'))
            payload = json.loads(self.rfile.read(length))
            logging.info(f"fields: {payload.keys()}")
            img_bytes = base64.b64decode(payload["Uploaded file"].encode('utf-8'))
            img = Image.open(io.BytesIO(img_bytes))
            img.save("received.jpg")
            class_name, score, embeddings = do_inference(img)
            logging.info(f"class_name: {class_name}, score: {score}, embeddings: {embeddings}")

        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))

def run_server(request_handler, port=8080):
    server_address = ('', port)
    server = HTTPServer(server_address, request_handler)
    logging.info('Starting server...\n')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
    logging.info('Stopping server...\n')

    

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    path_db = PATH_DB
    if not path_db.exists():
        conn = create_db(path_db)
    else:
        conn = sqlite3.connect(path_db)

    rows = conn.execute("SELECT _id, name, description, dangerous FROM animal ORDER BY _id")
    for row in rows:
        print(row)

    def request_handler_wrapper(*args):
        RequestHandler(conn, *args)
    run_server(request_handler_wrapper)
    conn.close()
