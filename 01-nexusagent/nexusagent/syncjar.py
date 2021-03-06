import shutil
import re
import tempfile
import requests
import time


from nexusagent.baseunit import ServiceUnit
from nexusagent.urltemplate import create_url_template
from nexusagent.baseuniterror import *


# from baseunit import ServiceUnit
# from urltemplate import create_url_template
# from baseuniterror import *

from requests_toolbelt import MultipartEncoder
from requests_toolbelt.auth.handler import AuthHandler


class SyncJar(ServiceUnit):
    """
    :type opts: dict
    :param opts:  

    :type project: str
    :param project: nexuse project name

    :type warehouse: tuple
    :param warehouse: save group and repository
    """
    def __init__(self, opts, project, warehouse):
        self.opts = opts
        self.project = project
        self.group, self.repository = warehouse  


    def query_jar(self, url):
        """ 
        query jar 
         
        :type url: str
        :param url: a url 
        """
        url = '{}/service/rest/v1/search?repository={}&group={}'.format(
                                                                   url, 
                                                                   self.repository, 
                                                                   self.group)
        jar_list = []
        self.opts['logger'].info('查询包地址 '+url)
        response = self.opts['session'].get(url, timeout=5)
        #print('+++++++++++++++')
        #self.opts['logger'].info(response)
        #self.opts['logger'].info(response.status_code)
        item_dic = {'items': response.json()['items']}
        response_continuationToken = response.json()['continuationToken']
         
        while response_continuationToken:
            # self.opts['logger'].info('query_url  '+url + '&continuationToken=%s' % response_continuationToken)
            #self.opts['logger'].info('开始进行token查询')
            response = self.opts['session'].get(url + '&continuationToken=%s' % response_continuationToken)
            #self.opts['logger'].info('查询返回码')
            #self.opts['logger'].info(response.status_code)
            #self.opts['logger'].info(response.json()) 
            item_dic['items'] = item_dic['items'] + response.json()['items']

            if response.json()['continuationToken'] == 'null':
                response_continuationToken = False
            else:
                response_continuationToken = response.json()['continuationToken']

        
        for i in item_dic['items']:
            for t in i['assets']:
                if bool(re.match('.*(\d+|RELEASE)\.jar$', t['downloadUrl'])):
                    jar_list.append(i['name'] + ':' + i['version'])

        self.opts['logger'].info("查询包数量为" + str(len(jar_list)) )
        return jar_list


    def diff_jar(self):
        """
        nexuse of the difference between the office and the remote, born 
        upload format
        """
        download_url = []
        update_set = set(self.tmpopts['office_jar']) - set(self.tmpopts['remote_jar'])
        self.opts['logger'].info('开始对比')
        if update_set:
            self.opts['logger'].info("Need_upload_list -- %s" % (update_set))
            self.opts['logger'].info('需要上传的列表数量为 %d' % len(update_set))

            for i in update_set:
                j_name, j_version = i.split(':')
                dl = {
                    'component_group': self.group,
                    'component_name': j_name,
                    'component_version': j_version,
                    'component_repository': self.repository}
                download_url.append(dl)
            self.tmpopts['download_url'] = download_url
        else:
            self.opts['logger'].info('没有可上传包列表')
            raise ValueNull('Need_upload_list -- []')


    
    def download_jar(self, dl):
        '''
        '''
        url = create_url_template(dl)
        self.opts['logger'].info('开始下载包 '+self.opts['nexus_office'] + url)
        response = requests.get(self.opts['nexus_office'] + url, timeout=5)
        data = response.json()['items']

        for t in data:
            # maven-snapshots not defind
            if bool(re.match('.*(\d+|RELEASE)\.jar$', t['downloadUrl'])):
                md5 = t['checksum']['md5']
                r = requests.get(t['downloadUrl'])
                with open(self.tmpopts['open_file'], 'wb') as f:
                    f.write(r.content)
        return md5


    def upload_jar(self, args):
        '''
        '''
        post_url = self.tmpopts['nexus_remote_url'] + '/service/rest/beta/components?repository=%s' % args['component_repository']
        auth = AuthHandler({post_url: (self.opts['nexus_user'], self.opts['nexus_password']),})

        time.sleep(5)
        self.opts['logger'].info('开始上传包 '+self.tmpopts['fullname_jar'])
        with open(self.tmpopts['open_file'], 'rb') as f:
            m = MultipartEncoder(fields={
                    'maven2.groupId': args['component_group'],
                    'maven2.artifactId': args['component_name'],
                    'maven2.version': args['component_version'],
                    'maven2.asset1.extension': 'jar',
                    'maven2.asset1': (self.tmpopts['fullname_jar'], f)},
                    boundary='------------%s' % hex(int(time.time() * 1000)))

            headers = {'Content-Type': m.content_type}
            r = requests.post(post_url, data=m, headers=headers, auth=auth)
            # self.opts['logger'].info(r.json())
            self.opts['logger'].info('上传结果')
            self.opts['logger'].info(r.content)
            code = str(r.status_code)
            self.opts['logger'].info('上传状态码 '+code)
            if code.startswith('2'):
                raise UploadSuccess('UploadSuccess: {} {}'.format(self.tmpopts['fullname_jar'], r.text))
            else:
                raise UploadError('UploadError: {} {}'.format(self.tmpopts['fullname_jar'], r.text))


#    def register_cmdb(self):
#        data = {
#            'u_name': self.tmpopts['fullname_jar'],
#            'u_checksum': self.tmpopts['md5'],
#        }
#        r = requests.post(self.opts['cmdb_url'] + '/upversion/', data=data, auth=(self.opts['cmdb_user'], self.opts['cmdb_password']))
#        code = str(r.status_code)
#        if code.startswith('2'):
#            self.opts['logger'].info('RegisterSuccess: {}'.format(self.tmpopts['fullname_jar']))
#        else:
#            self.opts['logger'].info('RegisterError: {} {}'.format(self.tmpopts['fullname_jar'], code.text))

   
    def tmpfile_dir(self):
        '''
        '''
        tmp_dir = tempfile.mkdtemp()
        self.tmpopts['tmp_dir'] = tmp_dir


    def run(self):
        '''
        '''
        self.opts['logger'].info('开始执行')
        self.tmpopts = {}
        self.tmpopts['nexus_remote_url'] = self.opts['nexus_remote'][self.project]['nexus_url']
        self.tmpopts['fail_upload'] = []
        try:
            self.opts['logger'].info(self.tmpopts['nexus_remote_url'])
            self.tmpopts['remote_jar'] = self.query_jar(self.tmpopts['nexus_remote_url'])
            self.tmpopts['office_jar'] = self.query_jar(self.opts['nexus_office'])

            self.diff_jar()
            self.tmpfile_dir()

            for index,data in enumerate(self.tmpopts['download_url']):
                try:
                    self.opts['logger'].info('开始上传第 %d 个包' % index)
                    self.opts['logger'].info('还剩 %d 个包' % (len(self.tmpopts['download_url'])-index))
                    self.tmpopts['fullname_jar'] = data['component_name'] + '-' + data['component_version'] + '.jar'
                    self.tmpopts['open_file'] = self.tmpopts['tmp_dir'] + '/' + self.tmpopts['fullname_jar']
                    self.tmpopts['md5'] = self.download_jar(data)
                    self.upload_jar(data)
                except UploadSuccess as e:
                    pass
                except UploadError as e:
                    self.tmpopts['fail_upload'].append(e)
            #self.send_sms(self.tmpopts['fail_upload'])
        except ValueNull as e:
            self.opts['logger'].info('SyncJar ValueNull: %s', e)
            return True 
        except Exception as e:
           self.opts['logger'].info('SyncJar Exception: %s', e)
        finally:
            self.opts['logger'].info('执行完成')
            if 'tmp_dir' in self.tmpopts:
                shutil.rmtree(self.tmpopts['tmp_dir'])
