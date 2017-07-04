import mei_video
import time
t = 'IGSC8a3bb97ec113f3530070851e20074363b4a0629af59f648bcba8bd081e2d4ac0%3ADFPJApOmZmB379IdSnVOQ2QNXjg5QtO8%3A%7B%22_auth_user_id%22%3A5387644807%2C%22_auth_user_backend%22%3A%22accounts.backends.CaseInsensitiveModelBackend%22%2C%22_auth_user_hash%22%3A%22%22%2C%22_token_ver%22%3A2%2C%22_token%22%3A%225387644807%3Ayd0uV4SxXa6p6460cKAucSMKtavBHWAM%3A1ee0a4554d0d39c8028df2a0937da33f2406b6ae62a8b368242df3d4e952163d%22%2C%22_platform%22%3A4%2C%22last_refreshed%22%3A1498812736.0128965378%2C%22asns%22%3A%7B%22time%22%3A1498812736%2C%2223.99.114.67%22%3A8075%7D%7D;'
for i in range(10):
    mei_video.test_new(t)
    time.sleep(60)
