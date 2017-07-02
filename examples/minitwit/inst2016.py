import  mei
import time
t = "IGSC341f55974baadb2775ff551acc9fb1625fb9466061411e4e6a8ad0cd8806d7c0%3AUQR4evOb50AbefuIH60POSuGzddobOKU%3A%7B%22asns%22%3A%7B%22time%22%3A1498550402%2C%2223.99.114.67%22%3A8075%7D%2C%22_auth_user_hash%22%3A%22%22%2C%22_auth_user_backend%22%3A%22accounts.backends.CaseInsensitiveModelBackend%22%2C%22_token%22%3A%222969173752%3AZOYZQFh3sPzMzvhXQ51CooOAbUVvhq8F%3A8b8c328f724c0df8c8cba73615054f50873ccdd33e8f3b6a97e5b222759cd654%22%2C%22_token_ver%22%3A2%2C%22_platform%22%3A4%2C%22_auth_user_id%22%3A2969173752%2C%22last_refreshed%22%3A1498550403.2377448082%7D;"

for i in range(10):
    mei.test_new(t)
    time.sleep(60)
