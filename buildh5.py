import h5py
import numpy as np
from PIL import Image
import sys
sys.path.insert(0, '/nfs/isicvlnas01/share/opencv-3.1.0/lib/python2.7/site-packages/')
import cv2
import io
import os


def main(depth_file, seg_file, dset_file, index):
    data_folder = '/nas/vista-ssd01/users/achingup/TDA/fayao-dcnf-fcsp-new/output/'

    image_folder_file = '/nas/vista-ssd01/users/achingup/run_job_base_dir/002-img_calc_stats/sequence/txt_files/new'+ str(index)

    # list_of_files = os.listdir(image_folder)



    # with open(data_folder+'/imnames.txt') as f:
    #     content = f.readlines()
    # content = [x.strip() for x in content]

    # content[1] = content[1][1:]
    # imagelist = []
    # #print content[1]
    # for count, elem in enumerate(content):
    #     if (count >1) :
    #         if(count%2 == 1):
    #             elem = elem[2:]
    #             #print elem
    #             imagelist.append(elem)
    _f = open(image_folder_file, 'r')

    imagelist = _f.readlines()

    outputfile = h5py.File('/nas/vista-ssd01/users/achingup/TDA/MySynthText/data/'+dset_file,'w')
    outputfile.create_group('image')
    outputfile.create_group('depth')
    outputfile.create_group('seg')

    #hdf5_file.create_dataset("train_img", train_shape, np.int8)

    imgcount = 0
    with h5py.File(data_folder+"/"+depth_file, "r") as depthdb:
        with h5py.File(data_folder+"/"+seg_file, "r") as segdb:

            for imagename in imagelist:
                try:
                    # filename = image_folder +"/"+ imagename.
                    filename = imagename.rstrip()
                    imagename = filename.split("/")[8]
                    print(">>>>>>",filename)
                    img = cv2.imread(filename, 1)
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # print(img.shape)
                    # input('waiting')
                    depth = depthdb[imagename]
                    seg = segdb['mask'][imagename]
                    outputfile['seg'].create_dataset(imagename,data=seg)
                    outputfile['seg'][imagename].attrs['area']=seg.attrs['area']
                    outputfile['seg'][imagename].attrs['label']=seg.attrs['label']
                    outputfile['depth'].create_dataset(imagename,data=depth)
                    outputfile['image'].create_dataset(imagename,data=img)
                    print "file succeeded: " + filename
                    imgcount += 1
                except Exception as e:
                    print imagename + " failed"
                    print e
    print str(imgcount) + " images succeeded"


# if __name__ == "__main__":
#     main()
