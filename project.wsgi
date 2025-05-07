import sys
import os

# تحديد المسار إلى تطبيق Flask
sys.path.insert(0, '/var/www/project')

from app import app as application
