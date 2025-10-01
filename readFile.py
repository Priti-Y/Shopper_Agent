# Function to read a file and return its contents
def readFile(sfilename):
    with open(sfilename, 'r') as f1:
        data = f1.read()
        print(data)
    return data