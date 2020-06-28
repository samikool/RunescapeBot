import argparse

from models import *  # set ONNX_EXPORT in models.py
from utils.datasets import *
from utils.utils import *

from time import sleep

class rune_model:
    opt = {}
    stuff = {}
    def __init__(self, 
                cfg='cfg/yolov3-spp.cfg', 
                names='data/coco.names', 
                weights='weights/yolov3-spp-ultralytics.pt', 
                source='data/samples', 
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
        webcam = source == '0' or source.startswith('rtsp') or source.startswith('http') or source.endswith('.txt')

        # Initialize
        device = torch_utils.select_device(opt.device)
        if os.path.exists(out):
            shutil.rmtree(out)  # delete output folder
        os.makedirs(out)  # make new output folder

        # Initialize model
        model = Darknet(opt.cfg, imgsz)

        # Load weights
        attempt_download(weights)
        if weights.endswith('.pt'):  # pytorch format
            model.load_state_dict(torch.load(weights, map_location=device)['model'])
        else:  # darknet format
            load_darknet_weights(model, weights)

        # Eval mode
        model.to(device).eval()

        save_img = True
        dataset = LoadImages(source, img_size=imgsz)

        # for path,img,im0s,vid_cap in dataset:
        #     print('Path: ', path)
        #     print('Image: ', img)
        #     print('Im0s: ', im0s)
        #     print('vid_cap: ', vid_cap)

        # Get names and colors
        names = load_classes(opt.names)
        colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(names))]

        self.stuff = {'imgsz':imgsz, 'names':names, 'colors':colors, 'device':device, 'model':model, 'opt':opt, 'dataset':dataset, 'webcam':webcam, 'out':out, 'save_txt':save_txt, 'save_img':save_img, 'view_img':view_img}
    
    def detect(self):
        #Run inference
        t0 = time.time()
        img = torch.zeros((1, 3, self.stuff['imgsz'], self.stuff['imgsz']), device=self.stuff['device'])  # init img
        _ = self.stuff['model'](img.float()) if self.stuff['device'].type != 'cpu' else None  # run once
        count = 0
        for path, img, im0s, vid_cap in self.stuff['dataset']:
            self.detect1(img, im0s, count)
            count+=1
            img = torch.from_numpy(img).to(self.stuff['device'])
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
                if self.stuff['webcam']:  # batch_size >= 1
                    p, s, im0 = path[i], '%g: ' % i, im0s[i].copy()
                else:
                    p, s, im0 = path, '', im0s

                save_path = str(Path(self.stuff['out']) / Path(p).name)
                s += '%gx%g ' % img.shape[2:]  # print string
                gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  #  normalization gain whwh
                if det is not None and len(det):
                    # Rescale boxes from imgsz to im0 size
                    det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                    # Print results
                    for c in det[:, -1].unique():
                        n = (det[:, -1] == c).sum()  # detections per class
                        s += '%g %ss, ' % (n, self.stuff['names'][int(c)])  # add to string

                    # Write results
                    for *xyxy, conf, cls in det:
                        if self.stuff['save_txt']:  # Write to file
                            xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                            with open(save_path[:save_path.rfind('.')] + '.txt', 'a') as file:
                                file.write(('%g ' * 5 + '\n') % (cls, *xywh))  # label format

                        if self.stuff['save_img'] or self.stuff['view_img']:  # Add bbox to image
                            label = '%s %.2f' % (self.stuff['names'][int(cls)], conf)
                            plot_one_box(xyxy, im0, label=label, color=self.stuff['colors'][int(cls)])

                # Print time (inference + NMS)
                print('%sDone. (%.3fs)' % (s, t2 - t1))

                # Stream results
                if self.stuff['view_img']:
                    cv2.imshow(p, im0)
                    if cv2.waitKey(1) == ord('q'):  # q to quit
                        raise StopIteration

                # Save results (image with detections)
                if self.stuff['save_img']:
                    if self.stuff['dataset'].mode == 'images':
                        cv2.imwrite(save_path, im0)
                    else:
                        if vid_path != save_path:  # new video
                            vid_path = save_path
                            if isinstance(vid_writer, cv2.VideoWriter):
                                vid_writer.release()  # release previous video writer

                            fps = vid_cap.get(cv2.CAP_PROP_FPS)
                            w = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            h = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                            vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*self.opt.fourcc), fps, (w, h))
                        vid_writer.write(im0)
            

        if self.stuff['save_txt'] or self.stuff['save_img']:
            print('Results saved to %s' % os.getcwd() + os.sep + self.stuff['out'])
            if platform == 'darwin':  # MacOS
                os.system('open ' + save_path)

        print('Done. (%.3fs)' % (time.time() - t0))

    def detect1(self, imgg, im0s, count):
        #Run inference
        t0 = time.time()
        img = torch.zeros((1, 3, self.stuff['imgsz'], self.stuff['imgsz']), device=self.stuff['device'])  # init img
        _ = self.stuff['model'](img.float()) if self.stuff['device'].type != 'cpu' else None  # run once
        
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
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class
                    s += '%g %ss, ' % (n, self.stuff['names'][int(c)])  # add to string

                # Write results
                for *xyxy, conf, cls in det:
                    if self.stuff['save_img'] or self.stuff['view_img']:  # Add bbox to image
                        label = '%s %.2f' % (self.stuff['names'][int(cls)], conf)
                        plot_one_box(xyxy, im0, label=label, color=self.stuff['colors'][int(cls)])

            # Print time (inference + NMS)
            print('%sDone. (%.3fs)' % (s, t2 - t1))

            # Save results (image with detections)
            cv2.imwrite('output/screenshot'+str(count)+'.png', im0)

        print('Done. (%.3fs)' % (time.time() - t0))
        input()


def load(opt,save_img=False):
    imgsz = (320, 192) if ONNX_EXPORT else opt.img_size  # (320, 192) or (416, 256) or (608, 352) for (height, width)
    out, source, weights, half, view_img, save_txt = opt.output, opt.source, opt.weights, opt.half, opt.view_img, opt.save_txt
    webcam = source == '0' or source.startswith('rtsp') or source.startswith('http') or source.endswith('.txt')

    # Initialize
    device = torch_utils.select_device(device='cpu' if ONNX_EXPORT else opt.device)
    if os.path.exists(out):
        shutil.rmtree(out)  # delete output folder
    os.makedirs(out)  # make new output folder

    # Initialize model
    model = Darknet(opt.cfg, imgsz)

    # Load weights
    attempt_download(weights)
    if weights.endswith('.pt'):  # pytorch format
        model.load_state_dict(torch.load(weights, map_location=device)['model'])
    else:  # darknet format
        load_darknet_weights(model, weights)

    # Second-stage classifier
    classify = False
    if classify:
        modelc = torch_utils.load_classifier(name='resnet101', n=2)  # initialize
        modelc.load_state_dict(torch.load('weights/resnet101.pt', map_location=device)['model'])  # load weights
        modelc.to(device).eval()

    # Eval mode
    model.to(device).eval()

    # Fuse Conv2d + BatchNorm2d layers
    # model.fuse()

    # Export mode
    if ONNX_EXPORT:
        model.fuse()
        img = torch.zeros((1, 3) + imgsz)  # (1, 3, 320, 192)
        f = opt.weights.replace(opt.weights.split('.')[-1], 'onnx')  # *.onnx filename
        torch.onnx.export(model, img, f, verbose=False, opset_version=11,
                          input_names=['images'], output_names=['classes', 'boxes'])

        # Validate exported model
        import onnx
        model = onnx.load(f)  # Load the ONNX model
        onnx.checker.check_model(model)  # Check that the IR is well formed
        print(onnx.helper.printable_graph(model.graph))  # Print a human readable representation of the graph
        return

    # Half precision
    half = half and device.type != 'cpu'  # half precision only supported on CUDA
    if half:
        model.half()

    # Set Dataloader
    vid_path, vid_writer = None, None
    if webcam:
        view_img = True
        torch.backends.cudnn.benchmark = True  # set True to speed up constant image size inference
        dataset = LoadStreams(source, img_size=imgsz)
    else:
        save_img = True
        dataset = LoadImages(source, img_size=imgsz)

    # Get names and colors
    names = load_classes(opt.names)
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(names))]

    return {'imgsz':imgsz, 'names':names, 'colors':colors, 'device':device, 'model':model, 'opt':opt, 'half':half, 'dataset':dataset, 'classify':classify, 'webcam':webcam, 'out':out, 'save_txt':save_txt, 'save_img':save_img, 'view_img':view_img}

def detect(imgsz, names, colors, device, model, opt, half, dataset, classify, webcam, out, save_txt, save_img, view_img):
    # Run inference
    t0 = time.time()
    img = torch.zeros((1, 3, imgsz, imgsz), device=device)  # init img
    _ = model(img.half() if half else img.float()) if device.type != 'cpu' else None  # run once
    for path, img, im0s, vid_cap in dataset:
        img = torch.from_numpy(img).to(device)
        img = img.half() if half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        # Inference
        t1 = torch_utils.time_synchronized()
        pred = model(img, augment=opt.augment)[0]
        t2 = torch_utils.time_synchronized()

        # to float
        if half:
            pred = pred.float()

        # Apply NMS
        pred = non_max_suppression(pred, opt.conf_thres, opt.iou_thres,
                                   multi_label=False, classes=opt.classes, agnostic=opt.agnostic_nms)

        # Apply Classifier
        if classify:
            pred = apply_classifier(pred, modelc, img, im0s)

        # Process detections
        for i, det in enumerate(pred):  # detections for image i
            if webcam:  # batch_size >= 1
                p, s, im0 = path[i], '%g: ' % i, im0s[i].copy()
            else:
                p, s, im0 = path, '', im0s

            save_path = str(Path(out) / Path(p).name)
            s += '%gx%g ' % img.shape[2:]  # print string
            gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  #  normalization gain whwh
            if det is not None and len(det):
                # Rescale boxes from imgsz to im0 size
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                # Print results
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class
                    s += '%g %ss, ' % (n, names[int(c)])  # add to string

                # Write results
                for *xyxy, conf, cls in det:
                    if save_txt:  # Write to file
                        xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                        with open(save_path[:save_path.rfind('.')] + '.txt', 'a') as file:
                            file.write(('%g ' * 5 + '\n') % (cls, *xywh))  # label format

                    if save_img or view_img:  # Add bbox to image
                        label = '%s %.2f' % (names[int(cls)], conf)
                        plot_one_box(xyxy, im0, label=label, color=colors[int(cls)])

            # Print time (inference + NMS)
            print('%sDone. (%.3fs)' % (s, t2 - t1))

            # Stream results
            if view_img:
                cv2.imshow(p, im0)
                if cv2.waitKey(1) == ord('q'):  # q to quit
                    raise StopIteration

            # Save results (image with detections)
            if save_img:
                if dataset.mode == 'images':
                    cv2.imwrite(save_path, im0)
                else:
                    if vid_path != save_path:  # new video
                        vid_path = save_path
                        if isinstance(vid_writer, cv2.VideoWriter):
                            vid_writer.release()  # release previous video writer

                        fps = vid_cap.get(cv2.CAP_PROP_FPS)
                        w = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        h = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*opt.fourcc), fps, (w, h))
                    vid_writer.write(im0)

    if save_txt or save_img:
        print('Results saved to %s' % os.getcwd() + os.sep + out)
        if platform == 'darwin':  # MacOS
            os.system('open ' + save_path)

    print('Done. (%.3fs)' % (time.time() - t0))

# if __name__ == '__main__':
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--cfg', type=str, default='cfg/yolov3-spp.cfg', help='*.cfg path')
#     parser.add_argument('--names', type=str, default='data/coco.names', help='*.names path')
#     parser.add_argument('--weights', type=str, default='weights/yolov3-spp-ultralytics.pt', help='weights path')
#     parser.add_argument('--source', type=str, default='data/samples', help='source')  # input file/folder, 0 for webcam
#     parser.add_argument('--output', type=str, default='output', help='output folder')  # output folder
#     parser.add_argument('--img-size', type=int, default=512, help='inference size (pixels)')
#     parser.add_argument('--conf-thres', type=float, default=0.3, help='object confidence threshold')
#     parser.add_argument('--iou-thres', type=float, default=0.6, help='IOU threshold for NMS')
#     parser.add_argument('--fourcc', type=str, default='mp4v', help='output video codec (verify ffmpeg support)')
#     parser.add_argument('--half', action='store_true', help='half precision FP16 inference')
#     parser.add_argument('--device', default='', help='device id (i.e. 0 or 0,1) or cpu')
#     parser.add_argument('--view-img', action='store_true', help='display results')
#     parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
#     parser.add_argument('--classes', nargs='+', type=int, help='filter by class')
#     parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
#     parser.add_argument('--augment', action='store_true', help='augmented inference')
#     opt = parser.parse_args()
#     opt.cfg = list(glob.iglob('./**/' + opt.cfg, recursive=True))[0]  # find file
#     opt.names = list(glob.iglob('./**/' + opt.names, recursive=True))[0]  # find file
#     print(opt)

#     with torch.no_grad():
#         detect()

def initialize(cfg='cfg/yolov3-spp.cfg', names='data/coco.names', weights='weights/yolov3-spp-ultralytics.pt', source='data/samples', output='output', img_size=512, conf_thres=0.3, iou_thres=0.6, fourcc='mp4v',half=False, device='', view_img=False, save_txt=False, classes='', agnostic_nms=False, augment=False):
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

    with torch.no_grad():
        stuff = load(opt=opt)
        detect(stuff['imgsz'], stuff['names'], stuff['colors'], stuff['device'], stuff['model'], stuff['opt'], stuff['half'], stuff['dataset'], stuff['classify'], stuff['webcam'], stuff['out'], stuff['save_txt'], stuff['save_img'], stuff['view_img'])

# initialize(cfg='cfg/yolov3-spp.cfg', names='data/custom/custom.names', weights='weights/last.pt', source='data/custom/test_images')

# rune_model = rune_model(cfg='cfg/yolov3-spp.cfg', 
#                         names='data/custom/custom.names', 
#                         weights='weights/last.pt', 
#                         source='data/custom/test_images')
# rune_model.load(rune_model.opt)
# rune_model.detect()