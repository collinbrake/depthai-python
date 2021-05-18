#!/usr/bin/env python3

import depthai as dai

# Start defining a pipeline
pipeline = dai.Pipeline()

# Define a source - color camera
cam = pipeline.createColorCamera()
cam.setBoardSocket(dai.CameraBoardSocket.RGB)
cam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)

# Create an encoder, consuming the frames and encoding them using H.265 encoding
videoEncoder = pipeline.createVideoEncoder()
videoEncoder.setDefaultProfilePreset(1920, 1080, 30, dai.VideoEncoderProperties.Profile.H265_MAIN)
cam.video.link(videoEncoder.input)

# Create output
videoOut = pipeline.createXLinkOut()
videoOut.setStreamName('h264')
videoEncoder.bitstream.link(videoOut.input)

# Connect and start the pipeline
with dai.Device(pipeline) as device:
    cnt = 0
    # Output queue will be used to get the encoded data from the output defined above
    q = device.getOutputQueue(name="h264", maxSize=30, blocking=True)

    try:
        while True:
            maxSize = 5 * 1024 * 1024 * 1024
            totalSizeReceived = 0
            # The .h264 file is a raw stream file (not playable yet)
            with open('video.h264', 'wb') as videoFile:
                print("Press Ctrl+C to stop encoding...")

                while totalSizeReceived < maxSize:
                    h264Packet = q.get()  # Blocking call, will wait until a new data has arrived
                    h264Data = h264Packet.getData()
                    h264Data.tofile(videoFile)  # Appends the packet data to the opened file
                    print(f"received {cnt} size {len(h264Data)}")
                    totalSizeReceived+=len(h264Data)
                    cnt+=1

    except KeyboardInterrupt:
        # Keyboard interrupt (Ctrl + C) detected
        pass

    print("To view the encoded data, convert the stream file (.h264) into a video file (.mp4) using a command below:")
    print("ffmpeg -framerate 30 -i video.h264 -c copy video.mp4")
