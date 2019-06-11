import h5py
import numpy as np
from PIL import Image
import cv2
import io

import os
import shutil

def  main():

    import argparse
    parser = argparse.ArgumentParser(description="enter the language. lang_es, lang_ja, lang_ko")
    parser.add_argument("lang", help="lang_ja,lang_ko,lang_es")
    args = parser.parse_args()
    outfile = 'results/SynthText_'+args.lang+'.h5'
    # outfile = '/nas/vista-ssd01/users/achingup/TDA/data/'+ 'SynthText_lang_es_bigger_dataset.h5'


    # if not os.path.exists("results/"+args.lang):
    #     os.makedirs("results/"+args.lang)
    if os.path.exists("results/" + args.lang):
        shutil.rmtree("results/"+args.lang)
    os.makedirs("results/"+args.lang)
    # create a specific directory of each language


    free_count = 0
    images_to_wr = 0

    with h5py.File(outfile, "r") as resdb:
        list_images = resdb['data'].keys()
        #resdb['data'][list_images[0]].attrs.keys())
        for images in list_images:
            
            img_array = np.array(resdb['data'][images])
            img = Image.fromarray(img_array, "RGB")
            img.save('results/'+args.lang+'/'+images+'.png')
            #img.show()

            # print('attributes = ',resdb['data'][images].attrs.get('charBB'))
            charBB = resdb['data'][images].attrs.get('charBB')
            lineBB = resdb['data'][images].attrs.get('lineBB')
            wordBB = resdb['data'][images].attrs.get('wordBB')

            char_array = resdb['data'][images].attrs.get('charArray')
            line_array = resdb['data'][images].attrs.get('lineArray')
            word_array = resdb['data'][images].attrs.get('wordArray')


            # do_something(charBB, char_array, wordBB, word_array, lineBB, line_array)
           

            free_count += 1
            if(free_count >  images_to_wr-1):
                inp = raw_input('continue? (number to continue, q to exit):')
                if inp == 'q':
                    break
                else:
                    images_to_wr = int(inp)
                    free_count = 0 

def do_something(charBB, char_array, wordBB, word_array, lineBB, line_array):

    top_left = 0
    top_right = 1
    bottom_right = 2
    bottom_left = 3
    x = 0
    y = 1

    lst_tuples = [(charBB, char_array),(wordBB, word_array),(lineBB, line_array)]

    # enter 0 for character, 1 for word and 2 for line.
    mode = 0 # change here
    current = lst_tuples[mode]

    for index, word in enumerate(current[1]):

        c_top_left = (current[0][x][top_left][index],current[0][y][top_left][index])
        c_top_right = (current[0][x][top_right][index],current[0][y][top_right][index])
        c_bottom_right = (current[0][x][bottom_right][index],current[0][y][bottom_right][index])
        c_bottom_left = (current[0][x][bottom_left][index],current[0][y][bottom_left][index])

        print('top_left = coordinates for word = ', word, 'are = ',c_top_left)
        print('top_right = coordinates for word = ', word, 'are = ',c_top_right)
        print('bottom_right = coordinates for word = ', word, 'are = ',c_bottom_right)
        print('bottom_left = coordinates for word = ', word, 'are = ', c_bottom_left)
        print("")


if __name__ == "__main__":
    main()
