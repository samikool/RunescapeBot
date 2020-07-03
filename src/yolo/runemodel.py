import argparse

from models import *
from utils.datasets import *
from utils.utils import *

from time import sleep

class rune_model:
    opt = {}
    stuff = {}
    def __init__(self, 
                cfg='cfg/yolov3-spp.cfg', 
                names='data/custom/custom.names', 
                weights='weights/best.pt', 
                source='data/custom/test_images', 
                output='output', 
                img_size=512, 
                conf_thres=0.3, 
                iou_thres=0.6, 
                fourcc='mp4v', 
                half=False, device='', 
                view_img=False, 
                save_txt=False, 
                classes='', 
                agnostic_nms=False, 
                augment=False):

        opt = argparse.ArgumentParser()
        
        opt.cfg = cfg
        opt.names = names
        opt.weights = weights
        opt.source = source
        opt.output = output
        opt.img_size = img_size
        opt.conf_thres = conf_thres
        opt.iou_thres = iou_thres
        opt.fourcc = fourcc
        opt.half = half
        opt.device = device
        opt.view_img = view_img
        opt.save_txt = save_txt
        opt.classes=classes
        opt.agnostic_nms = agnostic_nms
        opt.augment = augment

        opt.cfg = list(glob.iglob('./**/' + opt.cfg, recursive=True))[0]  # find file
        opt.names = list(glob.iglob('./**/' + opt.names, recursive=True))[0]  # find file

        self.opt = opt

    def load(self, opt, save_img=False):
        imgsz = opt.img_size  # (320, 192) or (416, 256) or (608, 352) for (height, width)
        out, source, weights, half, view_img, save_txt = opt.output, opt.source, opt.weights, opt.half, opt.view_img, opt.save_txt
        source == '0' or source.startswith('rtsp') or source.startswith('http') or source.endswith('.txt')

        # Initialize
        device = torch_utils.select_device(opt.device)
        if os.path.exists(out):
            shutil.rmtree(out)  # delete output folder
        os.makedirs(out)  # make new output folder

        # Initialize model
        model = Darknet(opt.cfg, imgsz)

        # Load weights
        if weights.endswith('.pt'):  # pytorch format
            model.load_state_dict(torch.load(weights, map_location=device)['model'])
        else:  # darknet format
            load_darknet_weights(model, weights)

        # Eval mode
        model.to(device).eval()

        save_img = True
        dataset = LoadImages(source, img_size=imgsz)

        # Get names and colors
        names = load_classes(opt.names)
        colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(names))]

        self.stuff = {'imgsz':imgsz, 'names':names, 'colors':colors, 'device':device, 'model':model, 'opt':opt, 'dataset':dataset, 'out':out, 'save_txt':save_txt, 'save_img':save_img, 'view_img':view_img}

    def detect(self, imgg, im0s, count):
        #Run inference
        t0 = time.time()

        img = torch.zeros((1, 3, self.stuff['imgsz'], self.stuff['imgsz']), device=self.stuff['device'])  # init img
        img = torch.from_numpy(imgg).to(self.stuff['device'])
        img = img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0

        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        # Inference
        t1 = torch_utils.time_synchronized()
        pred = self.stuff['model'](img, augment=self.opt.augment)[0]
        t2 = torch_utils.time_synchronized()

        # Apply NMS
        pred = non_max_suppression(pred, self.opt.conf_thres, self.opt.iou_thres,
                                multi_label=False, classes=self.opt.classes, agnostic=self.opt.agnostic_nms)
                                
        # Process detections
        for i, det in enumerate(pred):  # detections for image i
            s, im0 = '', im0s
            s += '%gx%g ' % img.shape[2:]  # print string

            gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  #  normalization gain whwh
            if det is not None and len(det):
                # Rescale boxes from imgsz to im0 size
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                # Print results
                # for c in det[:, -1].unique():
                #     n = (det[:, -1] == c).sum()  # detections per class
                #     s += '%g %ss, ' % (n, self.stuff['names'][int(c)])  # add to string

                objects={}
                j=0
                # Write results 
                for *xyxy, conf, cls in det:
                    objects[j] = {}
                    objects[j]['top'] = xyxy[0].item()
                    objects[j]['left'] = xyxy[1].item()
                    objects[j]['bottom'] = xyxy[2].item()
                    objects[j]['right'] = xyxy[3].item()
                    objects[j]['class'] = self.stuff['names'][int(cls)]
                    j+=1

                    if self.stuff['save_img'] or self.stuff['view_img']:  # Add bbox to image
                        label = '%s %.2f' % (self.stuff['names'][int(cls)], conf)
                        plot_one_box(xyxy, im0, label=label, color=self.stuff['colors'][int(cls)])
                
                print(objects)
                

            # Print time (inference + NMS)
            print('%sDone. (%.3fs)' % (s, t2 - t1))

            # Save results (image with detections)
            cv2.imwrite('output/screenshot'+str(count)+'.png', im0)

        print('Done. (%.3fs)' % (time.time() - t0))