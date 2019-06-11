# Author: Ankush Gupta
# Date: 2015
"Script to generate font-models."

import pygame
from pygame import freetype
from text_utils import FontState
import numpy as np 
import cPickle as cp
import argparse
from shutil import copyfile
import os


def main(LANG):
    print '\n ============================= \n'
    print 'Processing fonts'

    # 	LANG = LANG

    pygame.init()
    ys = np.arange(8,200)
    A = np.c_[ys,np.ones_like(ys)]

    xs = []
    models = {} #linear model

    FONT_LIST = os.path.join('data', 'fonts/fontlist_'+LANG+'.txt')
    fonts = [os.path.join('data','fonts',f.strip()) for f in open(FONT_LIST)]

    font_count = 0
    for i in xrange(len(fonts)):
        # print i
        font = freetype.Font(fonts[i], size=12)
        h = []
        for y in ys:
            h.append(font.get_sized_glyph_height(y))
        h = np.array(h)
        m,_,_,_ = np.linalg.lstsq(A,h)
        models[font.name] = m
        xs.append(h)
        font_count+=1

    print 'Font Processing success. Fonts processed = ', font_count
    print '\n ============================= \n'

    with open('data/models/font_px2pt_{}.cp'.format(LANG),'w') as f:
        cp.dump(models,f)
#     FS = FontState(LANG = LANG, data_dir = 'data')

#plt.plot(xs,ys[i])
#plt.show()
