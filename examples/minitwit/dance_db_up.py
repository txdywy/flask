with open('dance_pic','r') as f:
    new = f.readlines() 
new = [i.strip('\n') for i in new]
print new
from models.model_mei import *
for i in new:
    x = Dance(image_url=i)
    flush(x)


