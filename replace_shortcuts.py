import struct
import os
import shutil


# folder you want the replacements to be performed in
DIR = r"C:\Users\your\path\here"


def get_target(path):
    """takes in the path of a link file and returns the full path of the file it point to

    :param path: path of a link file
    :return: the target (str)
    """
    with open(path, 'rb') as stream:
        content = stream.read()

        # skip first 20 bytes (HeaderSize and LinkCLSID)
        # read the LinkFlags structure (4 bytes)
        lflags = struct.unpack('I', content[0x14:0x18])[0]
        position = 0x18

        # if the HasLinkTargetIDList bit is set then skip the stored IDList
        # structure and header
        if (lflags & 0x01) == 1:
            position = struct.unpack('H', content[0x4C:0x4E])[0] + 0x4E

        last_pos = position
        position += 0x04

        # get how long the file information is (LinkInfoSize)
        length = struct.unpack('I', content[last_pos:position])[0]

        # skip 12 bytes (LinkInfoHeaderSize, LinkInfoFlags, and VolumeIDOffset)
        position += 0x0C

        # go to the LocalBasePath position
        lbpos = struct.unpack('I', content[position:position + 0x04])[0]
        position = last_pos + lbpos

        # read the string at the given position of the determined length
        size = (length + last_pos) - position - 0x02
        temp = struct.unpack('c' * size, content[position:position + size])
        return ''.join([chr(ord(a)) for a in temp])


def replace_shortcuts(directory_path):
    """iterates over shortcut files in a directory and replaces them with copies of the actual files they point to

    :param directory_path: the path to the dir in wchich the replacements will take place
    """
    i = 1
    for filename in os.listdir(directory_path):
        f = os.path.join(directory_path, filename)

        if os.path.isfile(f) and f[-4:] == '.lnk':
            target = get_target(f)
            head, tail = os.path.split(target)
            shutil.copyfile(target, os.path.join(directory_path, tail))
            os.remove(f)
            print(f'{f} replaced (link {i})')

        i += 1


if __name__ == '__main__':
    subfolders = [f.path for f in os.scandir(DIR) if f.is_dir()]

    for folder in subfolders:
        print(f'REPLACING SHORTCUTS WITH SOURCE FILES IN {folder}...\n')
        replace_shortcuts(folder)
        print('\n')

    print('\nDONE')
    input('PRESS ANY KEY TO CONTINUE...')
