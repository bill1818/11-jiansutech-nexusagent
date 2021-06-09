import os
import json
import time
import psutil
import requests
import multiprocessing
import itertools

from nexusagent import syncjar 


class Manger:
    """
    The master server

    :type: dict
    :param: Load option from nagent.yml
    """
    def __init__(self, opts):
        self.opts = opts
        self.si = syncjar.SyncJar


    def cartesian_product_group_with_repository(self):
        """
        Create cartesian product 

        :rtype: dict
        :return: a and more project field
        """
        project_dic = {}
        for project in self.opts['nexus_remote']:
            group_list = self.opts['nexus_remote'][project]['nexus_group']
            repository_list = self.opts['nexus_remote'][project]['nexus_repository']
            cartesian_list = [x for x in itertools.product(group_list, repository_list)]
            project_dic[project] = cartesian_list

        
        return project_dic 


    def handle_jobs(self):
        """
        Instance syncjar object
        """
        try:
            # perform one or more warehouse to concur
            project_dic = self.cartesian_product_group_with_repository()
            for project in project_dic:
                for i in project_dic[project]:
                    # only accept a tuple eg: (group, repository)
                    self.opts['logger'].info('------------ %s %s' %  (project, i))
                    p = multiprocessing.Process(target=self.si(self.opts, project, i).run, args=())
                    p.start()
                    p.join()
        except Exception as e:
            self.opts['logger'].info('handle_jobs: {}' % e)
			

    def start(self):
        """Turn on the master server components
        """ 
        self.opts['logger'].info('Running -- the Nexus Manger')

        while True:
            try:
                self.handle_jobs()
                time.sleep(50)
            except Exception as e:
                self.opts['logger'].info(e)
