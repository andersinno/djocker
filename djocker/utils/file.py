import os

def find_filename(name, path):
    matches = []
    for root, dirs, files in os.walk(path):
        if name in files:
            matches.append(os.path.join(root, name))
    return matches
