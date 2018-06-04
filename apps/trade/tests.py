from django.test import TestCase

# Create your tests here.
import datetime,random
print(datetime.datetime.now().strftime('%y%m%d%H%M%S'))
print(datetime.datetime.now().strftime('%m-%d-%y %H:%M:%S'))
print(random.randint(10,100))