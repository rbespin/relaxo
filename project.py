#!/usr/bin/env python3
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
from multiprocessing import Process,Queue
import socket
import random
import time

# Now that I think about it, the socket between data_interface()
#   and data_processing might be completely unnecessary, and all functionality
#   achievable using a message queue
# At the very least, socket tutorial

# This function will talk to whatever process creates the data
# Idea 1: arduino generates data; that data is collected in this function
def data_interface(message_queue=None):
    print('[data_interface] function called!')
    times_called = 0
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('',61616))
    s.listen()
    conn,addr = s.accept()
    with conn:
        print('[data_interface] Connection received from data_processing!')
        while True:
            # Simulate the collecting of data
            time.sleep(0.5)
            random_num = random.randint(1,50)
            print('[data_interface] random_num: ', random_num)
            # Call this function only 80% of the time
            if random_num < 30:
                times_called += 1
                print('[data_interface] times_called: ', times_called)
                conn.sendall(str(random_num).encode())
                conn.recv(1)
            else:
                print('[data_interface] Retrying for valid data...')

# This function will talk to data_interface()
# Here, any processing of the data (machine learning, quantization, projections)
#   is processed here before sending off to data_rendering
def data_processing(message_queue=None):
    print('[data_processing] function called!')
    success = False
    while not success:
        try:
            s = socket.socket()
            s.connect(('',61616))
            success = True
        except:
            pass
    print('[data_processing] Connected to data_interface()!')
    # Forever listen to data_interface() for data
    while True:
        data = s.recv(1024)
        print('[data_processing] data: ', data.decode())
        # Data has been received... put it in message queue for data_rendering()
        message_queue.put(data.decode())
        s.sendall(bytes(1))


# This function will receive data from data_processing() and draw to figure
# For now, utilizes matplotlib's animation library
# There exists much better options; this just functions now
def data_rendering(message_queue=None):
    print('[data_rendering] function called!')
    #while True:
    #    data = message_queue.get()
    #    print('[data_rendering] message received in queue! data: ', data)

    fig,ax = plt.subplots(1,1,constrained_layout=True)
    data = []
    circle1 = None
    
    mappings = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1]
    print('len(mappings): ', len(mappings))

    def animation_fn(i):
        if i % 10 == 0:
            try:
                item = message_queue.get(block=False)
                print('[animation_fn] item: ', item)
                if len(data) == 15:
                    data.pop(0)
                data.append(int(item))
            except:
                pass
        #print('[animation_fn] data: ', data)
        ax.clear()
        ax.set_xlim((-1,1))
        ax.set_ylim((-1,1))
        if len(data) > 0:
            #print('i: ', i, ', data[0]: ', data[0])
            circle1 = plt.Circle((0, 0), (data[0]/30)*((mappings[i%30])/30), color='r',fill=False)
            ax.add_patch(circle1)
        #ax.plot(np.arange(len(data)), data)
    anim = animation.FuncAnimation(fig=fig,func=animation_fn,frames=30,interval=2)
    plt.show()


if __name__ == '__main__':
    # Universal message queue for 3 subprocesses
    mq = Queue()

    # Creating subprocesses
    p1 = Process(target=data_interface,args=(mq,))
    p2 = Process(target=data_processing,args=(mq,))
    p3 = Process(target=data_rendering,args=(mq,))

    # Starting
    p1.start()
    p2.start()
    p3.start()

    # Ending
    p1.join()
    p2.join()
    p3.join()
