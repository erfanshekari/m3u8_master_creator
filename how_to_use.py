# module required: opencv , ffmpeg
# run only on linux

import stream

(
    stream
    .stream('film.mp4')
    .encoder('360,480,720,1080')
)