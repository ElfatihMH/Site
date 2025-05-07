import os
from dotenv import load_dotenv
class Config:
    # إعدادات قاعدة البيانات
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'mysql+pymysql://suser:1234rty@localhost/subscription_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

