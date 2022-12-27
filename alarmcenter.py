import socket
import threading
import sys
import json
import datetime
import redis
import json
from pathlib import Path

if len(sys.argv) == 1 or len(sys.argv) > 2:
    print("not enough or too many arguments provided")
    sys.exit(1)
if not Path(sys.argv[1]).exists:
    print("specified config path (%s) does not exist. exiting." % sys.argv[1])

config = json.loads(Path(sys.argv[1]).read_text())

rediscon = redis.StrictRedis(config['redis_server_ip'], config['redis_server_port'])
p = rediscon.pubsub()
notification_channel = config['redis_channel']

camera_names = list()
camera_ips = list()

for k, v in config['cameras'].items():
    camera_names.append(k)
    camera_ips.append(v)

listen_port = config['alarm_listen_port']
logfile = config['alarm_logfile']

try:
    log = open(logfile, 'a')
except:
    sys.exit(1)


class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            client.settimeout(60)
            threading.Thread(target=self.listenToClient, args=(client, address)).start()

    def listenToClient(self, client, address):
        size = 1024
        while True:
            try:
                data = client.recv(size)
                if data:
                    # Set the response to echo back the recieved data
                    response = data
                    # print(str(dir(data)))
                    a = response

                    # self.target.write(str(response)).flush()
                    # client.send(response)
                else:
                    raise error('Client disconnected')
            except:
                client.close()
                return False
            obj = {}

            #obj['preamble'] = a[0:32].decode('UTF-8', 'ignore')
            obj['msg'] = a[32:].decode('UTF-8', 'ignore')
            temp = obj['msg'].rstrip('\r\n').split('\r\n')
            obj['nicemsg'] = {}
            for each in temp:
                obj['nicemsg'][each.split(':')[0]] = "".join(each.split(':')[1:])
            obj['nicemsg']['type'] = "dahua_alarm"
            obj['time'] = datetime.datetime.now().isoformat()
            if 'Channel' in obj['nicemsg'].keys():
                #obj['nicemsg']['camera_name'] = camera_names[int(obj['nicemsg']['Channel'])+1]
                obj['nicemsg']['camera_name'] = camera_names[int(obj['nicemsg']['Channel'])]
                obj['vendor'] = 'dahua'
                #obj['ip'] = camera_ips[int(obj['nicemsg']['Channel'])+1]
                obj['ip'] = camera_ips[int(obj['nicemsg']['Channel'])]
                obj['category'] = obj['nicemsg']['VideoAnalyseRule']
                obj['message'] = obj['nicemsg']['camera_name']
                rediscon.publish(notification_channel, json.dumps(obj))
            else:

                print("ERROR: 'Channel' not found in nicemsg:", json.dumps(obj))
            log.write(json.dumps(obj) + "\n")
            log.flush()

if __name__ == "__main__":
    while True:
        try:
            port_num = listen_port
            break
        except ValueError:
            pass

    ThreadedServer('', port_num).listen()
