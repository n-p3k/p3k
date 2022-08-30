import numpy as np
import sys
import geometry.mesh_utils as mu

def main():
    try:
        path1 = sys.argv[1]
        path2 = sys.argv[2]
        output = sys.argv[3]
    except:
        print("usage: merge file1 file2 ouputfile")
        exit(0)

    mu.merge_mesh_files(path1, path2, output) 
    print('done')
    
main()