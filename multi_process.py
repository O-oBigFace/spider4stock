from multiprocessing import Process, Lock
import time


def multi_process(function_name, begin, end, num_of_ps):
    count = end - begin
    quarter = count // num_of_ps
    lock = Lock()
    arglist = [(lock, begin + i * quarter, begin + (i + 1) * quarter) for i in range(num_of_ps)]
    print(arglist)

    for arg in arglist:
        process = Process(target=function_name, args=arg)
        process.start()
        time.sleep(3)
