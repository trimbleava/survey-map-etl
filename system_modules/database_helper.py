# standard libs
import os
import json
import logging

# third party libs
import pyodbc
import pandas as pd
from sqlalchemy import create_engine


# app modules
from system_modules import message_logger
message_logger.configure_logging()


class DatabaseHelper:
    def __init__(self, config_file="config.json"):
        self.config = self.loadJson(config_file)
        
    def loadJson(self, config_file="config.json"):
        try:
            with open(config_file, "r") as json_config:
                config_string = json_config.read()          
                data = json.loads(config_string)
                return data
        except Exception as e:
            msg = f"Error in lodaing {config_file}: {e}"
            logging.error(msg)

    def connectDB(self):
        try:
            connect_str = """
            DRIVER={ODBC Driver 17 for SQL Server};
            SERVER="""   + self.config['azure_sql_server']        + """;
            database=""" + self.config['azure_sql_db']            + """;
            Uid="""      + self.config['azure_sql_client_id']     + """;
            PWD={"""     + self.config['azure_sql_client_secret'] + """};
            Authentication=ActiveDirectoryServicePrincipal;
            Use Encryption for Data=true
            """
            logging.info("Connecting to database")
            return pyodbc.connect(connect_str)

        except Exception as e:
            msg = f"Error in connectDB: {e}"
            logging.error(msg)        
            raise Exception(msg)     

    
    def executeQuery(self, conn, query):
        cursor = None
       
        try:
            cursor  = conn.execute(query)
            columns = [column[0] for column in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            cursor.close()
            del cursor
            return pd.DataFrame(results)
        except Exception as e:
            if cursor:
                cursor.close()
                del cursor
            msg = f"Error in executeQuery(): {e}"
            logging.error(msg)          



# SqlAlchemy connect string format of the URL is an RFC-1738-style string.
class PostGISHelper():
    def __init__(self):
        self.user = os.getenv("HEATH_LS_ADMIN")
        self.password = os.getenv("HEATH_LS_ADMIN_PASS")
        self.host = os.getenv("DB_HOST")
        self.port = os.getenv("DB_PORT")
        self.database = os.getenv("HEATH_LS_DB")
       

    def connect(self):
        return create_engine(
            url="postgresql://{0}:{1}@{2}:{3}/{4}".format(
                self.user, self.password, self.host, self.port, self.database
            )
        )

