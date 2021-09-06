import os, glob

def clear():
    for f in glob.glob('./downloads/*'):
        os.remove(f)