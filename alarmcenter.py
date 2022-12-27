import socket
import threading
import sys
import json
import datetime
import redis
import json
from pathlib import Path


class ThreadedServer(object):
    def __init__(self, host, port, config, log, rediscon):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.notification_channel = config['redis_channel']
        self.log = log
        self.camera_names = list()
        self.camera_ips = list()
        self.rediscon = rediscon

        for k, v in config['cameras'].items():
            self.camera_names.append(k)
            self.camera_ips.append(v)

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
                obj['nicemsg']['camera_name'] = self.camera_names[int(obj['nicemsg']['Channel'])]
                obj['vendor'] = 'dahua'
                #obj['ip'] = camera_ips[int(obj['nicemsg']['Channel'])+1]
                obj['ip'] = self.camera_ips[int(obj['nicemsg']['Channel'])]
                obj['category'] = obj['nicemsg']['VideoAnalyseRule']
                obj['message'] = obj['nicemsg']['camera_name']
                self.rediscon.publish(self.notification_channel, json.dumps(obj))
            else:

                print("ERROR: 'Channel' not found in nicemsg:", json.dumps(obj))
            self.log.write(json.dumps(obj) + "\n")
            self.log.flush()

def main():
    if len(sys.argv) == 1 or len(sys.argv) > 2:
        print("not enough or too many arguments provided")
        sys.exit(1)
    if not Path(sys.argv[1]).exists:
        print("specified config path (%s) does not exist. exiting." % sys.argv[1])
        sys.exit(1)

    config = json.loads(Path(sys.argv[1]).read_text())

    try:
        print(config["alarm_logfile_path"])
        log = open(config['alarm_logfile_path'], 'a')
    except:
        print("Can't open alarmlog file (%s). exiting" % config['alarm_logfile_path'])
        sys.exit(1)

    rediscon = redis.StrictRedis(config['redis_server_ip'], config['redis_server_port'])
    p = rediscon.pubsub()

    ThreadedServer('', config['alarm_listen_port'], config, log, rediscon).listen()

if __name__ == "__main__":
    main()
