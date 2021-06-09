from nexusagent import config, manager, utils


class Manager:
    '''
    Creates a manager server
    '''
    def __init__(self):
        self.opts = config.manager_config('/etc/nagent/nagent.yml')


    def start(self):
        '''
        Run the sequence to start a serviceagent master server
        '''
        master = manager.Manger(self.opts)
        utils.daemonize()
        master.start()
