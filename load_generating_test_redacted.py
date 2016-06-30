# Basic Test Performance Script for Barbican
#
#   This script use multiprocessing pool/map functions,
#
#   Tests the amount of time it takes for Barbican to retrieve secrets
#   The secret refs are stored in a flat file which must be passed in as
#   a parameter.
#   2nd parameter is number-of-process will be spawned
#   Usage: python multiptocess-get_secrets.py 'secrets.txt' num-of-process

import sys
import time
import multiprocessing
from multiprocessing.dummy import Pool, Array
import requests
import json
import sys
from Queue import Queue
from threading import Thread
import itertools
import numpy

from datetime import date
from datetime import datetime

# global
start_tc = str(sys.argv[1])
end_tc = str(sys.argv[2])
total_time = []
create = []
verror = 0
cerror = 0
tenant_get_error_count = 0
tenant_get_process_times = []
tenant_list_error_count = 0
tenant_list_process_times = []
total_time = []
cerror_v2 = 0
create_v2_times = []
validate = []
auth_url = "REDACTED"
r = 0
end_create = 0
un = 0

def mean(lst):
    return float(sum(lst))/len(lst)

def perc90(lst):
    return numpy.percentile(lst,90,interpolation='higher')

def perc50(lst):
    return numpy.percentile(lst,50,interpolation='higher')

def create_v2_token():
    global cerror_v2, r, end_create
    authurl = auth_url + "/v2.0/tokens"
    req_body = {
        "auth": {
            "tenantName": "test_project",
            "passwordCredentials": {
                "username": "test_user",
                "password": "test"
            }
        }
    }



    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    start_create = time.time()
    #print "start v2"
    try:
        r = requests.post(authurl, data=json.dumps(req_body), headers=headers)
    except requests.exceptions.Timeout:
        print "timeout"
        cerror_v2 = cerror_v2 + 1
    except requests.exceptions.TooManyRedirects:
        print "too many redirects"
        cerror_v2 = cerror_v2 + 1
    except requests.exceptions.RequestException as e:
        print e
        print " Catastrophe!"
        cerror_v2 = cerror_v2 + 1
    else:
        end_create = time.time()
    if (r.status_code == 200 or r.status_code == 203):
        create_v2_times.append(end_create - start_create)
    else:
        print r.status_code

def tenant_get():
    global tenant_get_error_count, r, end_create
    tenant_id = "REDACTED"
    auth_url = "REDACTED"
    auth_url = auth_url + "/v2.0/tenants/" + tenant_id

    headers_val = {'content-type': 'application/json', 'Accept': 'application/json'}
    headers_val['X-Auth-Token'] = token
    start_time = time.time()
    try:
        r = requests.get(auth_url, headers=headers_val)
    except requests.exceptions.Timeout:
        print "timeout"
        tenant_get_error_count = tenant_get_error_count + 1
    except requests.exceptions.TooManyRedirects:
        print "too many redirects"
        tenant_get_error_count = tenant_get_error_count + 1
    except requests.exceptions.RequestException as e:
        print e
        print " Catastrophe!"
        tenant_get_error_count = tenant_get_error_count + 1
    else:
        end_time = time.time()
        if (r.status_code == 200):
            tenant_get_process_times.append(end_time - start_time)
        else:
            tenant_get_error_count = tenant_get_error_count + 1

def tenant_list():
    global tenant_list_error_count, r, end_create
    auth_url = "REDACTED"
    auth_url = auth_url + "/v2.0/tenants/"

    headers_val = {'content-type': 'text/plain', 'Accept-Charset': 'UTF-8'}
    headers_val['X-Auth-Token'] = token
    start_time = time.time()
    try:
        r = requests.get(auth_url, headers=headers_val)
    except requests.exceptions.Timeout:
        print "timeout"
        tenant_list_error_count = tenant_list_error_count + 1
    except requests.exceptions.TooManyRedirects:
        print "too many redirects"
        tenant_list_error_count = tenant_list_error_count + 1
    except requests.exceptions.RequestException as e:
        print e
        print " Catastrophe!"
        tenant_list_error_count = tenant_list_error_count + 1
    else:
        end_time = time.time()
        if (r.status_code == 200):
            tenant_list_process_times.append(end_time - start_time)
        else:
            tenant_list_error_count = tenant_list_error_count + 1

def create_v3token():
    global cerror, r, end_create, un
    #washdc creds
    authurl = "REDACTED"
    un = un + 1
    username = "load_user_" + str(un)
    req_body = { "auth": {
                     "identity": {
                         "methods": ["password"],
                         "password": {
                             "user": {
                                 "name": username,
                                 "domain": {"name":"default"},
                                 "password": "test"
                             }
                         }
                     }
                 }
    }

    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    start_create = time.time()
    try:
        r = requests.post(authurl, data=json.dumps(req_body), headers=headers)
    except requests.exceptions.Timeout:
        print "timeout"
        cerror = cerror + 1
    except requests.exceptions.TooManyRedirects:
        print "too many redirects"
        cerror = cerror + 1
    except requests.exceptions.RequestException as e:
        print e
        print " Catastrophe!"
        cerror = cerror + 1
    else:
        end_create = time.time()
    if (r.status_code == 201):
        token = r.headers['X-Subject-Token']
        create.append(end_create - start_create)
    else:
        print r.status_code

def validate_v3token():
    global verror, r, end_create

    #washdc creds
    authurl = "REDACTED/v3/auth/tokens"


    if token:
       headers_val = {'content-type': 'text/plain', 'Accept-Charset': 'UTF-8'}
       headers_val['X-Auth-Token'] = token
       headers_val['X-Subject-Token'] = token
       start_validate = time.time()
       try:
           r = requests.get(authurl, headers=headers_val)
       except requests.exceptions.Timeout:
           print "timeout"
           verror = verror + 1
       except requests.exceptions.TooManyRedirects:
           print "too many redirects"
           verror = verror + 1
       except requests.exceptions.RequestException as e:
           print e
           print " Catastrophe!"
           verror = verror + 1
       else:
           end_validate = time.time()
           if (r.status_code == 200):
                validate.append(end_validate - start_validate)
           else:
                verror = verror + 1


class CreateTokenV2Thread (Thread):
    def __init__(self, id, queue):
        Thread.__init__(self)
        self.id = id
        self.queue = queue

    def run(self):
        while True:
            start = time.time()
            ref = self.queue.get()
            create_v2_token()
            self.queue.task_done()
            end = time.time()
            diff_time = end - start
            total_time.append(diff_time)
           #print "v2token"



class TenantGetThread (Thread):
    def __init__(self, id, queue):
        Thread.__init__(self)
        self.id = id
        self.queue = queue

    def run(self):
        while True:
            start = time.time()
            ref = self.queue.get()
            tenant_get()
            self.queue.task_done()
            end = time.time()
            diff_time = end - start
            #print "tenantget"



class TenantListThread (Thread):
    def __init__(self, id, queue):
        Thread.__init__(self)
        self.id = id
        self.queue = queue

    def run(self):
        while True:
            start = time.time()
            ref = self.queue.get()
            tenant_list()
            self.queue.task_done()
            end = time.time()
            diff_time = end - start
            #print "tenantlist"




class CreateTokenV3Thread (Thread):
    def __init__(self, id, queue):
        Thread.__init__(self)
        self.id = id
        self.queue = queue

    def run(self):
        while True:
            start = time.time()
            ref = self.queue.get()
            create_v3token()
            #print "READ DONE ###"
            self.queue.task_done()
            end = time.time()
            diff_time = end - start
            total_time.append(diff_time)
            #print "create"




class ValidateTokenV3Thread (Thread):
    def __init__(self, id, queue):
        Thread.__init__(self)
        self.id = id
        self.queue = queue

    def run(self):
        while True:
            start = time.time()
            ref = self.queue.get()
            validate_v3token()
            #print "READ DONE ###"
            self.queue.task_done()
            end = time.time()
            diff_time = end - start
            total_time.append(diff_time)
            #print "validate"


def create_thread(threadid, num_thread):
    queue = Queue()
    threads = []
    for x in range(int(1 * num_thread)):
        #print "start v3 thread"
        worker = CreateTokenV3Thread(x, queue)
        worker.daemon = True
        threads.append(worker)
        worker.start()

    for i in range(int(1 * num_thread)):
        queue.put(i)

    for x in range(int(0 * num_thread)):
        worker = CreateTokenV2Thread(x, queue)
        worker.daemon = True
        threads.append(worker)
        worker.start()

    for i in range(int(0 * num_thread)):
        queue.put(i)

    for x in range(int(0 * num_thread)):
        worker = TenantListThread(x, queue)
        worker.daemon = True
        threads.append(worker)
        worker.start()

    for i in range(int(0 * num_thread)):
        queue.put(i)

    for x in range(int(0 * num_thread)):
        worker = TenantGetThread(x, queue)
        worker.daemon = True
        threads.append(worker)
        worker.start()

    for i in range(int(0 * num_thread)):
        queue.put(i)

    for x in range(int(0 * num_thread)):
        worker = ValidateTokenV3Thread(x, queue)
        worker.daemon = True
        threads.append(worker)
        worker.start()

    for i in range(int(0 * num_thread)):
        queue.put(i)

    queue.join()

def func_star(a_b):
    """Convert `f([1,2])` to `f(1,2)` call."""
    return create_thread(*a_b)

def main( numprocesses=10, num_times=1):
    global un
    for j in range(int(start_tc), int(end_tc)):
        un = 0
        num_times = 1
        threads_per_process = 10 * j

        for i in [1]:
            #print "### RUN #%d OF %d ###" % (i+1, num_times)

            arr = Array('i', range(numprocesses))

            # create a pool
            pool = Pool(processes=numprocesses)

            # start timer
            start = time.time()
            total_start = datetime.now()
            results = pool.map(func_star, itertools.izip(arr, itertools.repeat(threads_per_process)))
            pool.close
            pool.join

            total_end = datetime.now()
            end = time.time()
            diff_time = end - start


            print "Start time: " + str(total_start)
            print "End time: " + str(total_end)

        #total_end = time.time()


        #print "Start time: " + str(total_start)
        #print "End time: " + str(total_end)


        print "### SUMMARY AFTER %d iterations for concurrency %d ###" % (num_times , numprocesses * threads_per_process)
        print "Number of processes {}".format(numprocesses)
        print "Number of threads per process {}".format(threads_per_process)
        print "concurrency          : %s" % (numprocesses * threads_per_process)
        #print "no of first validation errors %d " % verror1
        print "no of create v3 error: %d" % cerror
        #print "no of validate v3 error: %d " % verror
        #print "no of tenant get error: %d" % tenant_get_error_count
        #print "no of tenant list error: %d" % tenant_list_error_count
        #print "no of create v2 error: %d" % cerror_v2

        print
        print "50th percentile across all iterations for   1st validate (in s): {} " .format(perc50(create))
        print "90th percentile across all iterations for  1st validate (in s): {} " .format(perc90(create))
        print "average across all iterations for  1st validate (in s): {} " .format(mean(create))
        print "max value for 1st validate (in s): {} " .format(max(create))
        print "min value for 2nd validate (in s): {} " .format(min(create))
        print
        print
        del total_time[:]
        del create[:]
        del tenant_get_process_times[:]
        del tenant_list_process_times[:]
        del total_time[:]
        del create_v2_times[:]
        del validate[:]

if __name__ == '__main__':
    main()