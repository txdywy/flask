from selenium import webdriver
service_args = [
    '--proxy=73.42.251.5:14497',
    '--proxy-type=socks5',
    ]
driver = webdriver.PhantomJS(service_args=service_args)
driver.set_window_size(1120, 550)
driver.get("http://goo.gl/oI4ehT")
print driver.current_url
driver.quit()




from selenium import webdriver
service_args = [
    '--proxy=73.42.251.5:14497',
    '--proxy-type=socks5',
    ]
driver = webdriver.PhantomJS(service_args=service_args)
driver.set_window_size(1120, 550)
driver.get("http://goo.gl/oI4ehT")
print driver.current_url
print driver.page_source
driver.quit()





from selenium import webdriver
driver = webdriver.Firefox()
driver.set_window_size(1120, 550)
driver.get("http://wtfismyip.com/text")
print driver.current_url
print driver.page_source
driver.quit()
