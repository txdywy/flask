from fabric.api import *
from config import *
local('mysql -h %s -u %s -p%s ' % (RDS_HOST, RDS_NAME, RDS_PASS, RDS_DB))
