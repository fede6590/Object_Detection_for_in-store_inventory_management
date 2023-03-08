from utils import settings
import os

dataset_path = settings.DATASET_PATH
source_path = os.path.join(dataset_path, 'images')

subset_path = settings.SUBSET_PATH
destination_path = os.path.join(subset_path, 'images')
os.makedirs(destination_path, exist_ok=True)

imgs_groups = ['train', 'val', 'test']
qnt_img_list =  [1515, 110, 375]
img_list=[[],[],[]]

for i in range(len(imgs_groups)):
    cnt=0
    n_img=0
    while(True):
        imgs = imgs_groups[i]+'_'+str(n_img)+'.jpg'
        src_imgs = os.path.join(source_path, imgs)
        dest_imgs = os.path.join(destination_path, imgs)
        print(dest_imgs)
        if os.path.exists(src_imgs):
            cnt+=1
            # img_list[i].append('./images/'+imgs_groups[i]+'_'+str(n_img)+'.jpg')
            img_list[i].append(os.path.join('./images', imgs_groups[i]+'_'+str(n_img)+'.jpg'))
            if os.path.exists(dest_imgs)==False:
                os.link(src_imgs, dest_imgs)
        n_img+=1
        if(cnt==qnt_img_list[i]):
            break

for i in range(len(imgs_groups)):
    with open(os.path.join(subset_path, imgs_groups[i]+'.txt'), "w") as f:
        for img in img_list[i]:
            f.write(img+'\n')