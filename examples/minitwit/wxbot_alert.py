import wxbot
import sys
name = sys.argv[1]
wxbot.add_alert(name)
wxbot.show_alert()
wxbot.main_loop()
