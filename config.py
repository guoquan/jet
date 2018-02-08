FLAGS = ['-nNT',] # no command, null stdin, no TTY
OPTS = {'TCPKeepAlive':'yes',
        'ServerAliveInterval':'30',
        'ServerAliveCountMax':'10',
        #'ExitOnForwardFailure':'yes'
       }

class Config(object):
    client = 'jet'
    client_args = {
        'server':'',
        'username':'',
        'password':'',
        'reverse':{
            '\*:80':'127.0.0.1:5000',
        },
        'flags':FLAGS,
        'options':OPTS,
    }
    monitors = {
        'alive_monitor':{
            'intervel':5,
            'retry_tol':0,
        },
        'http_monitor':{
            'intervel':15,
            'retry_tol':3,
            'url':'http://www.guoquan.net',
        },
        'process_monitor':{
            'intervel':5,
            'retry_tol':0,
        },
    }
