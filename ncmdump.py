# -*- coding: utf-8 -*-
"""
Created on Sun Jul 15 01:05:58 2018

@author: Nzix
"""

import binascii
import struct
import base64
import json
import os
import requests
from PIL import Image
from io import StringIO
import shutil
from Crypto.Cipher import AES
# you can directly import EasyID3 and ID3
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC

def dump(file_path):

    core_key = binascii.a2b_hex("687A4852416D736F356B496E62617857")
    meta_key = binascii.a2b_hex("2331346C6A6B5F215C5D2630553C2728")
    unpad = lambda s : s[0:-(s[-1] if type(s[-1]) == int else ord(s[-1]))]
    try:
        f = open(file_path,'rb')
    except IOError as e:
        print(e.errno)
        print(e)


    # magic header
    header = f.read(8)
    assert binascii.b2a_hex(header) == b'4354454e4644414d'

    # key data
    f.seek(2, 1)
    key_length = f.read(4)
    key_length = struct.unpack('<I', bytes(key_length))[0]

    key_data = bytearray(f.read(key_length))
    key_data = bytes(bytearray([byte ^ 0x64 for byte in key_data]))

    cryptor = AES.new(core_key, AES.MODE_ECB)
    key_data = unpad(cryptor.decrypt(key_data))[17:]
    key_length = len(key_data)

    # key box
    key_data = bytearray(key_data)
    key_box = bytearray(range(256))
    j = 0

    for i in range(256):
        j = (key_box[i] + j + key_data[i % key_length]) & 0xff
        key_box[i], key_box[j] = key_box[j], key_box[i]

    # meta data
    meta_length = f.read(4)
    meta_length = struct.unpack('<I', bytes(meta_length))[0]

    meta_data = bytearray(f.read(meta_length))
    meta_data = bytes(bytearray([byte ^ 0x63 for byte in meta_data]))
    meta_data = base64.b64decode(meta_data[22:])

    cryptor = AES.new(meta_key, AES.MODE_ECB)
    meta_data = unpad(cryptor.decrypt(meta_data)).decode('utf-8')[6:]
    meta_data = json.loads(meta_data)

    # crc32
    crc32 = f.read(4)
    crc32 = struct.unpack('<I', bytes(crc32))[0]

    # album cover
    f.seek(5, 1)
    image_size = f.read(4)
    image_size = struct.unpack('<I', bytes(image_size))[0]
    image_data = f.read(image_size)

    # media data
    file_name = meta_data['artist'][0][0] + ' - ' + meta_data['musicName'] + '.' + meta_data['format']
    new_file_path = os.path.join(os.path.split(file_path)[0],file_name)
    m = open(new_file_path,'wb')
    
    http = requests.urllib3.PoolManager()

    with http.request('GET', meta_data['albumPic'], preload_content=False) as r, open('img.jpg', 'wb') as out_file:       
        shutil.copyfileobj(r, out_file)
    img = open('img.jpg','rb')
        
    chunk = bytearray()
    while True:
        chunk = bytearray(f.read(0x8000))
        chunk_length = len(chunk)
        if not chunk:
            break

        for i in range(chunk_length):
            j = (i + 1) & 0xff
            chunk[i] ^= key_box[(key_box[j] + key_box[(key_box[j] + j) & 0xff]) & 0xff]

        m.write(chunk)

    m.close()
    f.close()
    
    # add music tag
    audio = EasyID3(new_file_path)
    audio['artist'] = meta_data['artist'][0][0]
    audio['title'] = meta_data['musicName']
    audio['album'] = meta_data['album']
    audio.save()
    
    audio = ID3(new_file_path)
    audio['APIC'] = APIC(
                          encoding=3,
                          mime='image/jpeg',
                          type=3, desc=u'Cover',
                          data=img.read()
                        ) 
    audio.save()
    

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_path = sys.argv[1:]
        directory = os.fsencode(file_path[0])
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.endswith(".ncm"):
                try:
                    dump(os.path.join(file_path[0], filename))
                except Exception as e:
                    print(e)
    else:
        print('please input file path!')
