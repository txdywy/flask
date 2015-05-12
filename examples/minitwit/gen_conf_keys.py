import config as c
d = dir(c)
d = [i for i in d if '__' not in i]
with open('config_template', 'w') as f:
    for i in d:
        f.write(i + " = ''\n")
 
