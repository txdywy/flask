rm alancer.db
python -c 'from model import *;init_db()'
python -c 'import import_project as i;i.load_all()'
