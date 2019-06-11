from __future__ import print_function, division
# Author: Ankush Gupta
# Date: 2015

"""
Entry-point for generating synthetic text images, as described in:

@InProceedings{Gupta16,
            author             = "Gupta, A. and Vedaldi, A. and Zisserman, A.",
            title                = "Synthetic Data for Text Localisation in Natural Images",
            booktitle        = "IEEE Conference on Computer Vision and Pattern Recognition",
            year                 = "2016",
        }
"""

import numpy as np
import h5py
import os, sys, traceback
import os.path as osp
from synthgen import RendererV3
from common import Color, colorize, colorprint
import wget, tarfile
import invert_font_size
import cropimages
from PIL import Image
sys.path.insert(0, '/nfs/isicvlnas01/share/opencv-3.1.0/lib/python2.7/site-packages/')
import cv2
import argparse

# global parameters
INSTANCE_PER_IMAGE = 1 # no. of times to use the same image
SECS_PER_IMG = 5 #max time per image in seconds
# url of the data (google-drive public file):
#DATA_URL = 'http://www.robots.ox.ac.uk/~ankush/data.tar.gz'
DATA_PATH='data'
def get_data(DB_FNAME):
    """
    Returns, the h5 database.
    """
    if not osp.exists(DB_FNAME):
        raise RuntimeError, "{} does not exist, STOP".format( DB_FNAME )
    # open the h5 file and return:
    if os.path.isfile( DB_FNAME ):
        return [h5py.File(DB_FNAME,'r')]
    elif os.path.isdir( DB_FNAME ):
        files = [ os.path.join(DB_FNAME, i) for i in os.listdir(DB_FNAME) if '.h5' in i ]
        print(files)
        res = [h5py.File(i,'r') for i in files]
        return res
    else:
        raise RuntimeError, 'Failed to read h5 files'

def add_res_to_db(imgname,res,db):
    """
    Add the synthetically generated text image instance
    and other metadata to the dataset.
    """
    ninstance = len(res)
    for i in xrange(ninstance):
        dname = "%s_%d"%(imgname, i)
        db['data'].create_dataset(dname,data=res[i]['img'])
        line_matrix, labels = cropimages.get_line_bb_matrix(dname, db['data'][dname][()], res[i]['wordBB'], res[i]['txt'])
        words, characters = get_words_and_characters(labels)
        db['data'][dname].attrs['charBB'] = res[i]['charBB']
        db['data'][dname].attrs.create('charArray', characters, dtype=h5py.special_dtype(vlen=unicode))
        db['data'][dname].attrs['wordBB'] = res[i]['wordBB']
        db['data'][dname].attrs.create('wordArray', words, dtype=h5py.special_dtype(vlen=unicode))
        db['data'][dname].attrs['lineBB'] = line_matrix
        db['data'][dname].attrs.create('lineArray', labels, dtype=h5py.special_dtype(vlen=unicode))

def save_res_images( imgname, lang, res ):
    ninstance = len(res)
    for i in xrange(ninstance):
        bbs = res[i]['wordBB'].transpose([2,0,1])
        img = res[i]['img'][...,::-1].copy()
        for r in bbs: # r is 2x4
            pt_lt, pt_rt, pt_rb, pt_lb = r.T # left top, right top, right bottom, left bottom
            x1 = min(pt_lt[0], pt_lb[0]); y1 = min(pt_lt[1], pt_rt[1])
            x2 = max(pt_rt[0], pt_rb[0]); y2 = max(pt_lb[1], pt_rb[1])
            img = cv2.rectangle(img, (x1, y1), (x2, y2), color=(0,0,255), thickness=3)
        outdir = '../debug/temp_images_{}/'.format(lang)
        if not os.path.exists( outdir ):
                os.makedirs( outdir )
        cv2.imwrite( os.path.join(outdir, '{}'.format(imgname)), img )
        # cv2.imwrite( '../debug/temp_images_{}/{}'.format(imgname), lang, img )

def get_words_and_characters(text):
    words, characters = [],[]
    for txt in text:
        t = txt.split(" ")
        for each_word in t:
            words.append(each_word)
            for c in each_word:
                characters.append(c)

    return words, characters

def main(DB_FNAME, OUT_FILE, lang, mode, viz=False):
    # invert_font_size.main(lang)
    # open databases:
    print(colorize(Color.BLUE,'getting data..',bold=True))
    db_list = get_data(DB_FNAME)
    print(db_list)
    print(colorize(Color.BLUE,'\t-> done',bold=True))

    # open the output h5 file:
    out_db = h5py.File(OUT_FILE,'w')
    out_db.create_group('/data')
    print(colorize(Color.GREEN,'Storing the output in: '+OUT_FILE, bold=True))
    global NUM_IMG
    cnt = 0
    for db in db_list:
        if cnt > NUM_IMG and NUM_IMG != -1:
            break
        # get the names of the image files in the dataset:
        imnames = sorted(db['image'].keys())
        N = len(imnames)
        start_idx,end_idx = 0,N

        RV3 = RendererV3(DATA_PATH,lang ,max_time=SECS_PER_IMG)

        for i in xrange(start_idx,end_idx):
            cnt += 1
#             if cnt < 964:
#                 continue # debugging
            if cnt > NUM_IMG and NUM_IMG != -1:
                break
            imname = imnames[i]
            try:
                # get the image:
                img = Image.fromarray(db['image'][imname][:])

                # get the pre-computed depth:
                #    there are 2 estimates of depth (represented as 2 "channels")
                #    here we are using the second one (in some cases it might be
                #    useful to use the other one):
                img_resize=img.resize(db['depth'][imname].shape) ###############
                depth = db['depth'][imname][:].T

                # get segmentation:
                seg = db['seg'][imname][:].astype('float32')
                area = db['seg'][imname].attrs['area']
                label = db['seg'][imname].attrs['label']

                # re-size uniformly:
                sz = depth.shape[:2][::-1]
                img = np.array(img.resize(sz,Image.ANTIALIAS))
                seg = np.array(Image.fromarray(seg).resize(sz,Image.NEAREST))


                # read the csv and get the populate the fint_temp dictionary
                font_temp = None

                print(colorize(Color.RED,'%d of %d'%(i,end_idx-1), bold=True))

                if mode == 'training' or mode == 'validation':
                    seed = None
                elif mode == 'testing':
                    seed = i
                else:
                    raise RuntimeError, 'Unrecognized mode: {}'.format( mode )
                res = RV3.render_text(imname, img,depth,seg,area,label, font_temp = font_temp ,lang=lang,
                                                            ninstance=INSTANCE_PER_IMAGE,viz=viz, seed = seed)
                if len(res) > 0:
                    # non-empty : successful in placing text:
                    add_res_to_db(imname,res,out_db)
                    if cnt < 500:
                        save_res_images( imname, lang,  res )
                # visualize the output:
                if viz:
                    if 'q' in raw_input(colorize(Color.RED,'continue? (enter to continue, q to exit): ',True)):
                        break
            except:
                traceback.print_exc()
                print(colorize(Color.GREEN,'>>>> CONTINUING....', bold=True))
                continue
        db.close()
    out_db.close()

def rgb2hsv(image):
    return image.convert('HSV')

def rgb2gray(image):
    rgb=np.array(image)
    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray

if __name__=='__main__':
    '''
    Usage python2 gen.py -lang lang_en -i input_file or dir -o output dir -num number of samples -mode training/validation/testing
    e.g. python2 gen.py -lang lang_en -i data/dset_training/ -o ../data/training/synthetic_en.h5 -num 50000 -mode training
    e.g. python2 gen.py -lang lang_en -i data/dset_validation/ -o ../data/validation/synthetic_en.h5 -num 50000 -mode testing
    '''
    parser = argparse.ArgumentParser(description='Genereate Synthetic Scene-Text Images')
    parser.add_argument("-lang", help="language to generate, e.g. lang_ja,lang_ko,lang_es")
    parser.add_argument("-i", dest='input', help="input_file or dir")
    parser.add_argument("-o", dest='output', help="output dir")
    parser.add_argument("-num", help='number of images')
    parser.add_argument("-mode", help='mode of generating')
    args = parser.parse_args()
    
    NUM_IMG = eval(args.num) # no. of images to use for generation (-1 to use all available):
    DB_FNAME = args.input # path to the data-file, containing image, depth and segmentation:
    OUT_FILE = args.output # output path to h5 file
    if not os.path.exists(os.path.dirname(OUT_FILE)):
        os.makedirs( os.path.dirname(OUT_FILE) )
    viz = False
    language = args.lang
    mode = args.mode
    # process font
    invert_font_size.main(language)
    print('MASTER - Fonts done')
    
    # process inpaint
    main(DB_FNAME, OUT_FILE, language, mode, viz)
    print('MASTER - gen done. Releasing resources now')

