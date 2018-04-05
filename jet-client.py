import multiprocessing
import subprocess
import time
import urllib2
import os
from config import Config

class Client(object):
    def __init__(self, command):
        self.command = command
        self.proc = None
        
    def is_alive(self):
        return self.proc and self.proc.poll() is None
    
    def pid(self):
        return self.proc.pid if self.proc else None
    
    def start(self):
        if not self.is_alive():
            print '[%s][Client %s]: Start.' % (time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), str(self))
            self.proc = subprocess.Popen(self.command)
        
    def stop(self, force=False):
        if self.is_alive():
            print '[%s][Client %s]: Stop.' % (time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), str(self))
            if force:
                self.proc.kill()
            else:
                self.proc.terminate()
        
    def restart(self, force=False):
        if self.is_alive():
            self.stop(force)
        self.start()
        
def jet_command(server, username, password, reverse, flags, options):
    command = ['sshpass',]
    if password:
        command.append('-p')
        command.append(password)
    command.append('ssh')
    for dest, src in reverse.iteritems():
        command.append('-R')
        command.append('%s:%s' % (dest, src))
    if username:
        command.append('-l')
        command.append(username)
    if flags:
        command.extend(flags)
    if options:
        for k, v in options.iteritems():
            command.append('-o')
            command.append('%s=%s' % (k,v))
    command.append(server)
    return command

class JetClient(Client):    
    def __init__(self, server, username, password, reverse, flags=None, options=None):
        command = jet_command(server, username, password, reverse, flags, options)
        Client.__init__(self, command)
    
class Monitor(multiprocessing.Process):
    def __init__(self, client, intervel, retry_tol=0):
        multiprocessing.Process.__init__(self)
        self.client = client
        self.intervel = intervel
        self.retry_tol = retry_tol
        self.retry = 0
        self.stopped = False
        
    def check_alive(self):
        pass
    
    def run(self):
        while not self.stopped:
            if self.check_alive():
                if self.retry >= self.retry_tol:
                    print '[%s][Monitor %s]: Client back alive from continuous (%d) down-time.' % (time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), str(self), self.retry)
                elif self.retry > 0:
                    print '[%s][Monitor %s]: Client back alive.' % (time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), str(self))
                self.retry = 0
            else:
                self.retry += 1
                print '[%s][Monitor %s]: Client down. Tol: %d/%d.' % (time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), str(self), self.retry, self.retry_tol)
                if self.retry >= self.retry_tol:
                    print '[%s][Monitor %s]: Restart client.' % (time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), str(self))
                    self.client.restart()
            time.sleep(self.intervel)
            
    def stop(self):
        self.stopped = True
    
class HttpMonitor(Monitor):
    def __init__(self, client, intervel, retry_tol, url):
        Monitor.__init__(self, client, intervel, retry_tol)
        self.url = url
        
    def check_alive(self):
        try:
            resp = urllib2.urlopen(self.url)
            if not resp.code == 200:
                raise urllib2.HTTPError()
        except:
            return False
        return True
    
class ProcessMonitor(Monitor):
    def __init__(self, client, intervel, retry_tol):
        Monitor.__init__(self, client, intervel, retry_tol)
        self.client_pid = client.pid()
        
    def check_alive(self):
        try:
            print self.client_pid
            os.kill(self.client_pid, 0) # check is exist
        except:
            return False
        return True
    
def main():
    config = Config()
    
    client = JetClient(**config.client_args)
    client.start()
    time.sleep(5)
    
    http_monitor = HttpMonitor(client, **config.monitors['http_monitor'])
    http_monitor.start()
    
    http_monitor.join()
    
if __name__ == '__main__':
    main()
