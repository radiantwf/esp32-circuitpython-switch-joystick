import numpy as np
from recognize import frame
from recognize.opencv.opencv import OpenCV


class NoneOpenCV(OpenCV):
    def __init__(self,frame:frame.Frame,opencv_processed_video_frame,controller_action_queue,log_udp_port):
        super().__init__(frame,opencv_processed_video_frame,controller_action_queue,log_udp_port)
        self._enable_send_action = False

    
    async def run(self):
        while True:
            data = await self._frame.get_frame()
            image = (
                np
                .frombuffer(data, np.uint8)
                .reshape([self._frame.height, self._frame.width, 3])
            )
            self._opencv_processed_video_frame.put(image.tobytes(),False,0)