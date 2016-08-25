import qy_util
import time
time.sleep(3)
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("123.125.114.144",80))
ip=s.getsockname()[0]
s.close()
qy_util.post(ip, touser='txdywy')
