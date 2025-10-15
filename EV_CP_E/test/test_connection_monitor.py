from ..monitor_connection import MonitorConnection

if __name__ == '__main__':
    con = MonitorConnection('localhost', 3440, None)
    con.run()