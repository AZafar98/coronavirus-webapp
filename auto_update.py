# Script to run daily so the webapp reloads when the data updates.

import os
os.utime('/var/www/azafar98_pythonanywhere_com_wsgi.py')