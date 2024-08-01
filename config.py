import os
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    MYSQL_HOST=os.getenv('DBEndpoint')
    MYSQL_USER = os.getenv('DBUser')
    MYSQL_PASSWORD = os.getenv('DBPassword')
    MYSQL_DB = os.getenv('DBName')
       
    # SECRET_KEY='flask_app'
    # MYSQL_HOST = 'localhost'
    # MYSQL_USER = 'root'
    # MYSQL_PASSWORD = 'password'
    # MYSQL_DB = 'flask'
