import os
from os import listdir


# Dashboard model
dashboards = [f for f in listdir((os.path.abspath(os.path.dirname(__file__))+'\dashboards').replace('\\', '/')) if f.endswith('.py')]
dash_choices = tuple([(v, v) for v in dashboards])

print(dash_choices)