
# coding: utf-8

# In[1]:


# utils.py
 
import time
import logging
import requests
import socket
import multiprocessing
 
class WebsiteDownException(Exception):
    pass
 
def ping_website(address, timeout=20):
    """
    Check if a website is down. A website is considered down 
    if either the status_code >= 400 or if the timeout expires
     
    Throw a WebsiteDownException if any of the website down conditions are met
    """
    try:
        response = requests.head(address, timeout=timeout)
        if response.status_code >= 400:
            logging.warning("Website %s returned status_code=%s" % (address, response.status_code))
            raise WebsiteDownException()
    except requests.exceptions.RequestException:
        logging.warning("Timeout expired for website %s" % address)
        raise WebsiteDownException()
    
def notify_owner(address):
    """ 
    Send the owner of the address a notification that their website is down 
     
    For now, we're just going to sleep for 0.5 seconds but this is where 
    you would send an email, push notification or text-message
    """
    logging.info("Notifying the owner of %s website" % address)
    time.sleep(0.5)
     
def check_website(address):
    """
    Utility function: check if a website is down, if so, notify the user
    """
    try:
        ping_website(address)
    except WebsiteDownException:
        notify_owner(address)


# In[2]:


WEBSITE_LIST = [
     'http://envato.com',
    'http://amazon.co.uk',
    'http://amazon.com',
    'http://facebook.com',
    'http://google.com',
    'http://google.fr',
    'http://google.es',
    'http://google.co.uk',
    'http://internet.org',
    'http://gmail.com',
    'http://stackoverflow.com',
    'http://github.com',
    'http://heroku.com',
    'http://really-cool-available-domain.com',
    'http://djangoproject.com',
    'http://rubyonrails.org',
    'http://basecamp.com',
    'http://trello.com',
    'http://yiiframework.com',
    'http://shopify.com',
    'http://another-really-interesting-domain.co',
    'http://airbnb.com',
    'http://instagram.com',
    'http://snapchat.com',
    'http://youtube.com',
    'http://baidu.com',
    'http://yahoo.com',
    'http://live.com',
    'http://linkedin.com',
    'http://yandex.ru',
    'http://netflix.com',
    'http://wordpress.com',
    'http://bing.com'
]


# ## Serial Approach
# 

# In[3]:


# serial_squirrel.py
 
import time

start_time = time.time()
 
for address in WEBSITE_LIST:
    check_website(address)
         
end_time = time.time()        
 
print("Time for SerialSquirrel: %ssecs" % (end_time - start_time))
 
# WARNING:root:Timeout expired for website http://really-cool-available-domain.com
# WARNING:root:Timeout expired for website http://another-really-interesting-domain.co
# WARNING:root:Website http://bing.com returned status_code=405
# Time for SerialSquirrel: 15.881232261657715secs


# ## Threading Approach
# We're going to get a bit more creative with the implementation of the threaded approach. We're using a queue to put the addresses in and create worker threads to get them out of the queue and process them. We're going to wait for the queue to be empty, meaning that all the addresses have been processed by our worker threads.

# In[4]:


# threaded_squirrel.py
 
import time
from queue import Queue
from threading import Thread
 
NUM_WORKERS = 16
task_queue = Queue()
 
def worker():
    # Constantly check the queue for addresses
    while True:
        address = task_queue.get()
        check_website(address)
         
        # Mark the processed task as done
        task_queue.task_done()
        
start_time = time.time()
         
# Create the worker threads
threads = [Thread(target=worker) for _ in range(NUM_WORKERS)]
 
# Add the websites to the task queue
[task_queue.put(item) for item in WEBSITE_LIST]
 
# Start all the workers
[thread.start() for thread in threads]
 
# Wait for all the tasks in the queue to be processed
task_queue.join()
 
         
end_time = time.time()        
 
print("Time for ThreadedSquirrel: %ssecs" % (end_time - start_time))
 
# WARNING:root:Timeout expired for website http://really-cool-available-domain.com
# WARNING:root:Timeout expired for website http://another-really-interesting-domain.co
# WARNING:root:Website http://bing.com returned status_code=405
# Time for ThreadedSquirrel: 3.110753059387207secs


# ## concurrent.futures
# As stated previously, concurrent.futures is a high-level API for using threads. The approach we're taking here implies using a ThreadPoolExecutor. We're going to submit tasks to the pool and get back futures, which are results that will be available to us in the future. Of course, we can wait for all futures to become actual results.
# 
# 

# In[5]:


# future_squirrel.py
 
import time
import concurrent.futures
 
NUM_WORKERS = 16
 
start_time = time.time()
 
with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
    futures = {executor.submit(check_website, address) for address in WEBSITE_LIST}
    concurrent.futures.wait(futures)
    
end_time = time.time()        
 
print("Time for FutureSquirrel: %ssecs" % (end_time - start_time))
 
# WARNING:root:Timeout expired for website http://really-cool-available-domain.com
# WARNING:root:Timeout expired for website http://another-really-interesting-domain.co
# WARNING:root:Website http://bing.com returned status_code=405
# Time for FutureSquirrel: 1.812899112701416secs


# ## The Multiprocessing Approach
# The multiprocessing library provides an almost drop-in replacement API for the threading library. In this case, we're going to take an approach more similar to the concurrent.futures one. We're setting up a multiprocessing.Pool and submitting tasks to it by mapping a function to the list of addresses (think of the classic Python map function).

# In[6]:


NUM_WORKERS = 16
 
start_time = time.time()
 
with multiprocessing.Pool(processes=NUM_WORKERS) as pool:
    results = pool.map_async(check_website, WEBSITE_LIST)
    results.wait()

end_time = time.time()         
print("Time for MultiProcessingSquirrel: %ssecs" % (end_time - start_time))
