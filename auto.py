import multi_process
import process
import sys

if __name__ == '__main__':
    begin = int(sys.argv[1])
    end = int(sys.argv[2])
    nop = int(sys.argv[3])

    multi_process.multi_process(function_name=process.spider, begin=begin, end=end, num_of_ps=nop)