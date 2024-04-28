import psycopg2
import redis
import time
import json
import socket
import os
import logging
from psycopg2 import sql, DatabaseError
from redis.exceptions import ConnectionError

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def open_db_connection():
    while True:
        try:
            connection = psycopg2.connect(f"user='{os.getenv('DB_USER')}' host='{os.getenv('DB_HOST')}' password='{os.getenv('DB_PASS')}'")
            cursor = connection.cursor()
            cursor.execute(sql.SQL("""
                CREATE TABLE IF NOT EXISTS votes (
                    id VARCHAR(255) NOT NULL UNIQUE,
                    vote VARCHAR(255) NOT NULL
                )"""))
            connection.commit()
            logging.info("Connected to db")
            return connection
        except psycopg2.OperationalError:
            logging.warning("Waiting for db")
            time.sleep(1)

def open_redis_connection():
    while True:
        try:
            r = redis.Redis(host='redis', decode_responses=True)
            r.ping()
            logging.info("Connected to redis")
            return r
        except ConnectionError:
            logging.warning("Waiting for redis")
            time.sleep(1)

def get_ip(hostname):
    try:
        ip_address = socket.gethostbyname(hostname)
        logging.info(f"IP address for {hostname} is {ip_address}")
        return ip_address
    except socket.gaierror as e:
        logging.error(f"Error retrieving IP for hostname {hostname}: {str(e)}")
        raise

def update_vote(connection, voter_id, vote):
    cursor = connection.cursor()
    try:
        cursor.execute(sql.SQL(f"INSERT INTO votes (id, vote) VALUES ('{voter_id}', '{vote}') ON CONFLICT(id) DO UPDATE SET vote = '{vote}', id = '{voter_id}'"))
    except DatabaseError as e:
        connection.rollback()
        logging.error(f"Database error: {e}")
    else:
        connection.commit()
        logging.info(f"Vote updated in database for voter ID {voter_id}")
    finally:
        cursor.close()

def main():
    try:
        pgsql = open_db_connection()
        redis_conn = open_redis_connection()

        while True:
            time.sleep(0.1)  # Slow down the loop to prevent CPU spikes

            json_data = redis_conn.lpop("votes")
            if json_data is not None:
                vote_data = json.loads(json_data)
                logging.info(f"Processing vote for '{vote_data['vote']}' by '{vote_data['voter_id']}'")
                if pgsql.closed:
                    logging.info("Reconnecting DB")
                    pgsql = open_db_connection()
                update_vote(pgsql, vote_data['voter_id'], vote_data['vote'])
            else:
                # Keep alive for the database
                pgsql.poll()
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        return 1

if __name__ == "__main__":
    main()
