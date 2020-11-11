import cv2, numpy as np, pandas as pd, os
from PIL import Image
from time import time, sleep
import shutil 


def space_shot():
    cam0 = cv2.VideoCapture(0)
    # cam1 = cv2.VideoCapture(1)
    #cam2 = cv2.VideoCapture(2)
    # cv2.namedWindow("test")
    img_counter = 0
    while True:
        ret0, frame0 = cam0.read()
        # ret1, frame1 = cam1.read()
        #ret2, frame2 = cam2.read()
        #gray0 = cv2.cvtColor(frame0, 0)
        #gray1 = cv2.cvtColor(frame1, 0)
        #gray2 = cv2.cvtColor(frame2, 0)    
        cv2.imshow("test1", frame0)
        #cv2.imshow("test2", frame1)
        #cv2.imshow("test3", gray2)
        #output = np.hstack((gray0, gray1, gray2))
        #if not ret0 + ret1 + ret2 == 3:
         #  break
        k = cv2.waitKey(1)
        if k%256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break
        elif k%256 == 32:
            # SPACE pressed
            img_name = "black_stain_{}.png".format(img_counter)
            cv2.imwrite(img_name, frame0)
            img_counter += 1
            print("{} written!".format(img_name))
            '''
            img_name = "opencv_frame_{}.png".format(img_counter)
            cv2.imwrite(img_name, frame0)
            print("{} written!".format(img_name))'''
            #break
    cam0.release()
    #cam1.release()
    #cam2.release()
    cv2.destroyAllWindows()




def set_res(cap, x,y):
    cap.set(cv2.CV_CAP_PROP_FRAME_WIDTH, int(x))
    cap.set(cv2.CV_CAP_PROP_FRAME_HEIGHT, int(y))
    return str(cap.get(cv2.CV_CAP_PROP_FRAME_WIDTH)),str(cap.get(cv2.CV_CAP_PROP_FRAME_HEIGHT))




def taking_shots(folder, how_many, step=0.5):
    os.chdir('../' + folder)
    cnt = []
    for _ in os.listdir():
        cnt.append(int(_.split('.')[0].split('_')[-1]))
    # cv2.namedWindow("test")
    try:
        img0_counter = max(cnt) + 1
    except:
        img0_counter =0
    img1_counter = img0_counter + 1
    tar = how_many + img0_counter
    
    cam0 = cv2.VideoCapture(0)
    # cam1 = cv2.VideoCapture(1)
    while True:
        ret0, frame0 = cam0.read()
        # ret1, frame1 = cam1.read()
        # frame0 = cv2.rotate(frame0, cv2.ROTATE_90_CLOCKWISE)
        cv2.imshow("test1", frame0)
        # cv2.imshow("test2", frame1)
        if not ret0:
           break    
        k = cv2.waitKey(1)
        if k%256 == 27 or img0_counter == tar or img1_counter == tar:
            # ESC pressed
            print("Escape hit, closing...")
            break
        
        sleep(step)
        img0_name = folder + "_{}.png".format(img0_counter)
        # img1_name = folder + "_{}.png".format(img1_counter)
        cv2.imwrite(img0_name, frame0)
        # cv2.imwrite(img1_name, frame1)
    
        img0_counter += 1
        # img1_counter = img0_counter + 1
        print("{} written!".format(img0_name))
        # print("{} written!".format(img1_name))
    cam0.release()
    cv2.destroyAllWindows()




space_shot()
taking_shots(folder='duanmian', how_many=500, step=0.1)

yamian
ranhei
duanmian


cam0 = cv2.VideoCapture('Taipei Shilin Nightmarket walking.mp4')
root = '../02_image/'
# for _ in os.listdir():
#    cnt.append(int(_.split('.')[0].split('_')[-1]))
# cv2.namedWindow("test")
# img_counter = max(cnt) + 1
img_counter = 0
frame_cnt = 0
while True:
    ret0, frame0 = cam0.read()
    if not ret0:
       break    
    k = cv2.waitKey(1)
    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    if frame_cnt % 40 == 0:
        img_name = '200125_shilin_nightmarket_IMG_{}.png'.format(str(img_counter).rjust(5, '0'))
        # cv2.imwrite(os.path.join(root, img_name), np.array(Image.fromarray(frame0).resize((640, 480), Image.LANCZOS).rotate(0, expand=1)))
        cv2.imwrite(os.path.join(root, img_name), np.array(Image.fromarray(frame0).rotate(0, expand=1)))
        img_counter += 1
        print("{} written!".format(img_name))
        if img_counter == 5999:
            break
    frame_cnt += 1

cam0.release()
cv2.destroyAllWindows()


Image.fromarray(frame0).show()


\


cnt = 0
for folder in ['001', '002', '003', '004', '005']:
    for each_pic in os.listdir(folder):
        new_name = 'aggregation_' + str(cnt).rjust(4, '0') + '.png'
        shutil.copyfile(os.path.join(folder, each_pic), os.path.join('aggregation', new_name))
        cnt += 1
        
for _, each_pic in enumerate(os.listdir()):
    # new_name = each_pic.split('.')[0] + '_inhalf.png'
    # Image.open(each_pic).resize((240, 320), Image.LANCZOS).save(os.path.join('../', 'aggregation_320_240', new_name))
    # Image.open(each_pic).resize((224, 320), Image.LANCZOS).save(each_pic)
    # shutil.copyfile(os.path.join(folder, each_pic), os.path.join('../', 'aggregation_320_240', new_name))
    #Image.open(each_pic).rotate(270).save(each_pic.split('.')[0] + '.png')
    #os.unlink(each_pic)
    # Image.open(each_pic).rotate(180, expand=True).resize((224, 320), Image.LANCZOS).save('xx_' + each_pic)
    
    img_size = (640, 480)  # (528 224)
    im = Image.open(each_pic)
    if im.size != img_size:
        im.resize(img_size, Image.LANCZOS).save('xxx_' + each_pic)
    if _ % 200 == 0:
        print('{:,}'.format(_))






def trans_loc(x1, y1, x2, y2):
    x1, x2 = int(round(x1 / 640 * 480)), int(round(x2 / 640 * 480))
    y1, y2 = int(round(y1 / 480 * 640)), int(round(y2 / 480 * 640))
    return x1, y1, x2, y2


im = Image.open(r'C:\Users\User\Desktop\pictures\aggregation\aggregation_0060.png')
im.resize((480, 640), Image.LANCZOS).save(r'C:\Users\User\Desktop\trans.png')

im = cv2.imread(r'C:\Users\User\Desktop\pictures\aggregation\aggregation_0071.png', 0)
im = np.array(Image.fromarray(im).resize((480, 640), Image.LANCZOS))
x1, y1, x2, y2 = trans_loc(237,	122, 300, 128)
cv2.rectangle(im, (x1, y1), (x2, y2), (0, 0, 0), 2)


Image.fromarray(im).show()




import pandas as pd, os, numpy as np


for each_xml in os.listdir():
    with open('xz_'+ each_xml, 'w') as w:
        with open(each_xml, 'r') as r:
            for _ in r:
                _ = _.replace('><', '>||<')
                temp = _.split('||')
                break
    break
                




with open(r'C:\Users\User\Desktop\01_annotations_aug_imgs.txt', 'w') as w:
    w.write('file_name,xmin,ymin,xmax,ymax,category\n')
    for each_xml in os.listdir():
        with open(each_xml, 'r') as r:
            file_name = ''
            params = []
            width, height = 0, 0
            for rows in r:
                rows = rows.replace('><', '>||<')
                rows = rows.split('||')
                for row in rows:
                    if '<name>' in row:
                        category = row.replace('<name>', '').replace('</name>', '').strip()
                        
                    if file_name == '':
                        if '<filename>' in row:
                            file_name = row.replace('<filename>', '').replace('</filename>', '').strip()
                            each_param = ['', '', '', '', '']
                            # >> [xmin, ymin, xmax, ymax]
                    else:

                        for i, each_tag in enumerate(['xmin', 'ymin', 'xmax', 'ymax']):
                            if '<' + each_tag + '>' in row:
                                if i in [0, 2]:
                                    each_param[i] = \
                                    str(int(round(int(row.replace('<' + each_tag + '>', '').replace('</' + each_tag + '>', '').strip()))))
                                else:
                                    each_param[i] = \
                                    str(int(round(int(row.replace('<' + each_tag + '>', '').replace('</' + each_tag + '>', '').strip()))))
                        if each_param[-2] != '':
                            each_param[-1] = category
                            params.append(each_param)
                            each_param = ['', '', '', '', '']
                            # category = ''
            for each_param in params:
                w.write(file_name + ',' + ','.join(each_param) + '\n')












df = pd.read_csv(r'C:\Users\User\Desktop\01_annotations_aug_imgs.txt')
df.columns = ['path', 'xmin', 'ymin', 'xmax', 'ymax', 'cate']
# for i in [1, 3]:
#    df[df.columns[i]] = np.round(df[df.columns[i]].astype(float) / 224 * 224).astype(int).astype(str)
# for i in [2, 4]:
#    df[df.columns[i]] = np.round(df[df.columns[i]].astype(float) / 528 * 512).astype(int).astype(str)
df.path = './images/' + df.path
df.loc[:, 'cate'] = 0
# df.cate[df.loc[:, 'cate'] == 'basketball_EdonyAI'] = 0
# df.cate[df.loc[:, 'cate'] == 'warriors_EdonyAI'] = 1
# df.cate[df.loc[:, 'cate'] == 'lakers_EdonyAI'] = 2
df.cate[df.loc[:, 'cate'] == 'nut_front'] = 0
df.cate[df.loc[:, 'cate'] == 'nut_back'] = 1


df = pd.read_csv(r'C:\Users\User\Desktop\01_annotations.txt')
df.columns = ['path', 'xmin', 'ymin', 'xmax', 'ymax', 'cate']
for each_key in ratio.keys():
    x, y = ratio[each_key]
    for i in [1, 3]:
        df[df.columns[i]][df.path.str[:7] == df.path.str[:5] + each_key] = \
        np.round(df[df.columns[i]][df.path.str[:7] == df.path.str[:5] + each_key].astype(float) / x * 576).astype(int).astype(str)
    for i in [2, 4]:
        df[df.columns[i]][df.path.str[:7] == df.path.str[:5] + each_key] = \
        np.round(df[df.columns[i]][df.path.str[:7] == df.path.str[:5] + each_key].astype(float) / y * 352).astype(int).astype(str)
df.path = r'C:/Users/User/Desktop/HollywoodHeads/JPEGImages/' + df.path

df.loc[:, 'cate'] = 0



img = cv2.imread('20200315_vid2_0083_01.jpg', 1)
a1, a2, a3, a4 = 435, 400, 681, 428
cv2.rectangle(img, (a1, a2), (a3, a4), (0, 255, 0), 2)
a1, a2, a3, a4 = 952, 429, 967, 440
cv2.rectangle(img, (a1, a2), (a3, a4), (0, 255, 0), 2)
a1, a2, a3, a4 = 891, 531, 1017, 560
cv2.rectangle(img, (a1, a2), (a3, a4), (0, 255, 0), 2)
Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).show()



with open(r'C:\Users\User\Desktop\01_annotations_aug_imgs.txt', 'w') as w:
    for uni_path in df.path.unique():
        tdf = df[df.path==uni_path]
        if not tdf.shape[0] > 1:
            w.write(uni_path + ' ' + ','.join(tdf.loc[tdf.index[0]][1:].astype(str).tolist()) + '\n')
        else:
            _ = uni_path
            for i in tdf.index.tolist():
                _ = _ + ' ' + ','.join(tdf.loc[i][1:].astype(str).tolist())
            w.write(_ + '\n')
            
df = pd.read_excel(r'C:\Users\User\Desktop\02_annotations.xlsx')



for each_pic in os.listdir():
    os.rename(each_pic, each_pic.replace('appended_4', 'appended_5'))
    



for i in range(526):
    x1, y1, x2, y2 = df.iloc[i, [1, 2, 3, 4]].tolist()
    #print(df.iloc[i, [1, 2, 3, 4]].tolist())
    x1, y1, x2, y2 = trans_loc(x1, y1, x2, y2)
    df.loc[i, 'xmin'] = x1
    df.loc[i, 'ymin'] = y1
    df.loc[i, 'xmax'] = x2
    df.loc[i, 'ymax'] = y2
    
    #print(df.iloc[i, [1, 2, 3, 4]].tolist())
    #break
    
df.to_excel(r'C:\Users\User\Desktop\02_annotations_2.xlsx', index=False)
    
    



