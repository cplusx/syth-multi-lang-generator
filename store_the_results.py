import os
import csv
import hashlib
from PIL import Image

class SavingResults:

    current_data_path = 'isi_data/'
    image = None
    outfile = None
    lang = None
    bb = None
    text = None
    md5 = None

    def __init__(self, lang):
        self.lang = lang
        self.do_file_folder_setup()
        self.outfile = open(os.path.join(self.current_data_path, 'annotation.csv'), 'w')
        fields = ['file_name', 'cwl','trans','at', 'md5hash', 'c0_tl', 'c1_tr', 'c2_br', 'c3_bl',]
        self.writer = csv.DictWriter(self.outfile, delimiter=',', lineterminator='\n', fieldnames=fields)
        self.writer.writeheader()

    
    def set_image(self, image):
        print('setting image')
        self.image = image
        self.md5 = hashlib.md5(image.tobytes()).hexdigest()
        

    def save_image(self, image):
        img = Image.fromarray(image, "RGB")
        img.save(self.current_data_path+"/"+self.md5+'.png')

        
    def do_file_folder_setup(self):
        self.current_data_path += self.lang
        self.create_directory(self.current_data_path)
        
    
    def write_this_data(self, bb, text):
        self.save_character_level(bb, text)
        self.save_word_level(bb, text)
        self.save_line_level(bb, text)

    def save_word_level(self, bb, text):

        # print(text)
        # print(bb)

        dic = dict()
        dic['file_name'] = self.md5+'.png'
        dic['cwl'] = 'w'
        dic['md5hash'] = self.md5

        index = 0

        top_left = 0
        top_right = 1
        bottom_right = 2
        bottom_left = 3

        word = ""
        starting_index = 0
        # space ord(char) == 32 
        # newline ord(char) == 10 , and ord(char) != 32)
        text += " "
        for char in text:
            if((ord(char) == 32 or ord(char) == 10) and len(word) > 0):
                dic['trans'] = self.charwise_hex_string(word)
                dic['at'] = word.encode('utf-8')
                dic['c0_tl'] = bb[:,top_left,starting_index]
                dic['c1_tr'] = bb[:,top_right,index-1]
                dic['c2_br'] = bb[:,bottom_right,index-1]
                dic['c3_bl'] = bb[:,bottom_left,starting_index]
                self.writer.writerow(dic)
                starting_index = index
                word=""
            elif (ord(char) != 32 and ord(char) != 10) :
                word += char
                index += 1
    
    def save_line_level(self, bb, text):

        # print(text)
        # print(bb)

        dic = dict()
        dic['file_name'] = self.md5+'.png'
        dic['cwl'] = 'l'
        dic['md5hash'] = self.md5

        index = 0

        top_left = 0
        top_right = 1
        bottom_right = 2
        bottom_left = 3

        word = ""
        starting_index = 0
        # space ord(char) == 32 
        # newline ord(char) == 10 , and ord(char) != 32)
        text += "\n"
        for char in text:
            if((ord(char) == 10) and len(word) > 0):
                dic['trans'] = self.charwise_hex_string(word)
                dic['at'] = word.encode('utf-8')
                dic['c0_tl'] = bb[:,top_left,starting_index]
                dic['c1_tr'] = bb[:,top_right,index-1]
                dic['c2_br'] = bb[:,bottom_right,index-1]
                dic['c3_bl'] = bb[:,bottom_left,starting_index]
                self.writer.writerow(dic)
                starting_index = index
                word=""
            elif (ord(char) != 10) :
                word += char
                if(ord(char) != 32):
                    index += 1

    def save_character_level(self, bb, text):
        dic = dict()
        dic['file_name'] = self.md5+'.png'
        dic['cwl'] = 'c'
        dic['md5hash'] = self.md5

        index = 0

        top_left = 0
        top_right = 1
        bottom_right = 2
        bottom_left = 3

        for char in text:
            if(ord(char) != 10 and ord(char) != 32):
                dic['at'] = char.encode('utf-8')
                dic['trans'] = self.charwise_hex_string(char)
                dic['c0_tl'] = bb[:,top_left,index]
                dic['c1_tr'] = bb[:,top_right,index]
                dic['c2_br'] = bb[:,bottom_right,index]
                dic['c3_bl'] = bb[:,bottom_left,index]
                self.writer.writerow(dic)
                index+=1

    def all_done_wind_up(self):
        self.outfile.close()

    def create_directory(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def charwise_hex_string(self, item):
        final = ''
        first_time = True
        for elem in range(len(item)):
            dec_value = ord(item[elem])
            hex_value = hex(dec_value)
            hex_value = hex_value[2:]  #0xff
            if len(hex_value) < 4:
                hex_value = '0'*(4 - len(hex_value)) + hex_value
            hex_value = 'u' + hex_value
            if first_time:
                final = hex_value
                first_time = False
            else:
                final = final + '_' + hex_value
        split_final = final.split('_u0020_')
        split_final = ' u0020 '.join(split_final)

        return split_final