import tensorrt as trt
import pycuda.autoinit
import pycuda.driver as cuda
import cv2
import numpy as np

class Processor():
    def __init__(self):
        logger = trt.Logger(trt.Logger.INFO)
        model = 'models/yolov5s-simple-2.trt'

        with open(model, 'rb') as f, trt.Runtime(logger) as runtime:
            engine = runtime.deserialize_cuda_engine(f.read())
       
        self.context = engine.create_execution_context()

        # allocate memory
        inputs, outputs, bindings = [], [], []
        stream = cuda.Stream()
        for binding in engine:
            size = trt.volume(engine.get_binding_shape(binding)) # * \
                   # engine.max_batch_size
            dtype = trt.nptype(engine.get_binding_dtype(binding))
            host_mem = cuda.pagelocked_empty(size, dtype)
            device_mem = cuda.mem_alloc(host_mem.nbytes)
            bindings.append(int(device_mem))
            if engine.binding_is_input(binding):
                inputs.append({ 'host': host_mem, 'device': device_mem })
            else:
                outputs.append({ 'host': host_mem, 'device': device_mem })
            
        # save to class
        self.inputs = inputs
        self.outputs = outputs
        self.bindings = bindings
        self.stream = stream
    
    def detect(self, img):
        img = self.pre_process(img)
        print('pre processed img', img)
        return img

    def pre_process(self, img):
        print('img shape 0', img.shape)
        img = cv2.resize(img, (640, 640)) 
        img = img.transpose((2, 0, 1))
        img = np.ascontiguousarray(img)
        return img

