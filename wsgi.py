import sys
import os

# تحديد المسار إلى البيئة الافتراضية
activate_this = '/var/www/project/venv/bin/activate_this.py'

# إضافة مسار المشروع إلى sys.path
sys.path.insert(0, '/var/www/project')

from app import app as application

