import bisect
from collections import defaultdict
import functools
import itertools
import json
import struct
from sys import argv
import threading
from execution_tree import BranchTree, BranchData

# Define constants
#define MAX_FORCED_FORKS 3
#define BDATA_SIZE 16
#define SHD_SIZE (4+MAX_FORCED_FORKS*128*BDATA_SIZE) //__PTHREAD_MUTEX_SIZE__
MAX_FORCED_FORKS = 3
BRANCH_DATA_SIZE = 16
PATH_LEN = 128
SHARED_DATA_SIZE = PATH_LEN * MAX_FORCED_FORKS * BRANCH_DATA_SIZE + 4  # Assuming mutex size is 8 bytes (e.g., on 64-bit systems)

# Define the SharedData class
class SharedData:
    def __init__(self, mutex, fork_count, exec_path, jmp_list, ret_list):
        self.mutex = mutex  # For simplicity, we just store the mutex bytes
        self.fork_count = fork_count
        self.exec_path = exec_path
        self.jmp_list = jmp_list
        self.ret_list = ret_list

    @classmethod
    def from_binary(cls, data):
        # Unpack the mutex (8 bytes), fork_count (1 byte), and exec_path
        mutex_size = struct.calcsize('Q')  # Assuming 8 bytes for mutex
        fork_count = int.from_bytes(data[:1], byteorder='big')
        exec_path_data = data[1:]
        assert len(exec_path_data) >= MAX_FORCED_FORKS * PATH_LEN * BRANCH_DATA_SIZE, f"Have len {len(exec_path_data)} (expect {MAX_FORCED_FORKS * PATH_LEN * BRANCH_DATA_SIZE})"
        exec_path = []
        for i in range(MAX_FORCED_FORKS):
            exec_path_row = []
            for j in range(128):
                offset = (i * 128 + j) * BRANCH_DATA_SIZE
                branch_data = BranchData.from_binary(exec_path_data[offset:offset + BRANCH_DATA_SIZE])
                exec_path_row.append(branch_data)
            exec_path.append(exec_path_row)

        return cls(0, fork_count, exec_path)

# Function to parse SharedData from a binary file
def parse_shared_data_from_file(filename):
    with open(filename, 'r') as file:
        f_content = file.read()
        json_dict = json.loads(f_content)
        return SharedData(fork_count=json_dict['fork_count'], 
                   exec_path=[list(map(lambda x: BranchData(flags=x['data'],**x), x)) for x in json_dict['exec_path']],
                   jmp_list=json_dict['jmp_list'],
                   ret_list=json_dict['ret_list'],
                   mutex=None)

# Example usage
if __name__ == "__main__":
    shared_data = parse_shared_data_from_file(argv[1])

    # Access parsed attributes
    print("Mutex (as bytes):", shared_data.mutex)
    print("Fork Count:", shared_data.fork_count)
    bt = BranchTree()
    branch_dict = defaultdict(lambda:0)
    dst_list: list[int] = []
    loc_list: list[int] = []
    normal_connection = []
    for i in range(MAX_FORCED_FORKS):
        bt.add_path(filter(lambda x: x.valid,shared_data.exec_path[i]))
        for x in filter(lambda x: x.valid,shared_data.exec_path[i]):
            branch_dict[x] += 1
            dst_list.append(x.dst)
            loc_list.append(x.loc)
    dst_list = sorted(list(set(dst_list))) #TODO sorted_set?
    print(shared_data.ret_list)
    ret_list = sorted(list(set(itertools.chain(*shared_data.ret_list))))
    print(shared_data.jmp_list)
    jmp_list = sorted(list(set(map(lambda x: tuple(x),itertools.chain(*shared_data.jmp_list)))))
    all_jmp_loc = []
    for i in jmp_list:
        all_jmp_loc.append(i[0])
        all_jmp_loc.append(i[1])
        dst_list.append(i[1])
    all_loc_list = sorted(list(set(itertools.chain(loc_list, dst_list, ret_list, all_jmp_loc)))) #TODO sorted_set?
    for i, d in enumerate(dst_list):
        index = bisect.bisect_right(all_loc_list, d)
        # Check if the index is within bounds, if it is, return the element at that index
        if index < len(all_loc_list):
            normal_connection.append((d,all_loc_list[index]))
        else:
            normal_connection.append((d,"end"))
    bt.visualize_tree2(branch_dict, normal_connection, jmp_list, ret_list)
