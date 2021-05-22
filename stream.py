# module required: opencv , ffmpeg
# run only on linux
from pathlib import Path
import ffmpeg as fmg
import cv2
class stream:
    def __init__(self,file_path):
        self.file_path = str(file_path)
        self.input = fmg.input(file_path)
        self.q360 = {'width': '640','height': '360','b:v': '800k'}
        self.q480 = {'width': '854','height': '480','b:v': '1200k'}
        self.q720 = {'width': '1280','height': '720','b:v': '1500k'}
        self.q1080 = {'width': '1920','height': '1080','b:v': '4000k'}
        # Parse input File
        self.input_cv2 = cv2.VideoCapture(self.file_path)
        self.input_fps = self.input_cv2.get(cv2.CAP_PROP_FPS)
        self.input_probe = fmg.probe(self.file_path)
        self.input_parse = next((stream for stream in self.input_probe['streams'] if stream['codec_type'] == 'video'),None)
        try:
            self.input_duration = float(self.input_parse['duration'])
        except:
            self.get_video_duration = self.input_parse['tags']
            self.video_duration_time_format = self.get_video_duration['DURATION']
            self.video_duration_h = int(self.video_duration_time_format[:2])
            self.video_duration_m = int(self.video_duration_time_format[3:5])
            self.video_duration_s = float(self.video_duration_time_format[6:])
            self.input_duration = ((self.video_duration_h / 60) + self.video_duration_m) * 60 + self.video_duration_s
        finally:
            pass
        self.trim_distance = self.input_fps * 10
        self.input_frames = int(self.input_cv2.get(cv2.CAP_PROP_FRAME_COUNT))
        self.input_fname = self.file_path[:-4].replace(' ','-')
        pass
        self.save_Path = Path.cwd() / 'stream' / self.input_fname / 'trimmed'
        try:
            self.save_Path.mkdir(parents=True,exist_ok=True)
            self.project_path = str(self.save_Path.parents[1]) + '/' + self.input_fname
        finally:
            pass
    
    # encode in any quality

    def encode_processor(self,called_quality,q_width,q_height,q_bv,q_ba):
            self.called_quality = called_quality
            self.q_width = q_width
            self.q_height = q_height
            self.q_bv = q_bv
            self.q_ba = q_ba
            # Start Process
            self.frames_vprs = self.input_frames
            self.cut_counter_vprs = float(0)
            self.name_counter_vprs = int(0)
            self.m3u8_vprsls = ['#EXTM3U','#EXT-X-VERSION:3','#EXT-X-PLAYLIST-TYPE:VOD','#EXT-X-TARGETDURATION:10']
            self.input_vprs = fmg.input(self.file_path)
            while self.frames_vprs > 0:
                self.sf_vprs = int(0)
                self.sfc_vprs = (self.sf_vprs + self.trim_distance) * self.cut_counter_vprs
                if self.sfc_vprs == 0:
                    self.sfc_vprs = 1
                else:
                    pass
                self.sf_vprs += self.trim_distance
                self.efc_vprs = self.sfc_vprs + self.trim_distance
                self.sf_a_vprs = float(0)
                self.sfc_a_vprs = (self.sf_a_vprs + (self.trim_distance / self.input_fps)) * self.cut_counter_vprs
                if self.sfc_a_vprs == 0:
                    self.sfc_a_vprs = 1
         
                self.efc_a_vprs = self.sfc_a_vprs + (self.trim_distance / self.input_fps)
                self.video_vprs = self.input_vprs.video.filter('fps',fps=24,round='up').filter('scale',width=self.q_width,height=self.q_height).trim(start_frame=self.sfc_vprs,end_frame=self.efc_vprs)
                self.audio_vprs = self.input_vprs.audio.filter('atrim',start=self.sfc_a_vprs,end=self.efc_a_vprs)
                (
                    fmg
                    .concat(self.video_vprs,self.audio_vprs,v=1,a=1)
                    .output(str(self.save_Path) + '/' + self.called_quality + '-' + str(self.name_counter_vprs) + '.ts',vcodec='h264',acodec='aac', **{'b:v':self.q_bv})
                    .overwrite_output()
                    .run()
                )
                self.frames_vprs = self.frames_vprs - self.trim_distance
                self.cut_counter_vprs += 1
                self.name_counter_vprs += 1
                self.sf_a_vprs += (self.trim_distance / self.input_fps)
                if self.frames_vprs > self.trim_distance:
                    self.m3u8_vprsls.append('#EXTINF:10.000,')
                    self.m3u8_vprsls.append(self.called_quality + '-' + str(self.name_counter_vprs) + '.ts')
                else:
                    self.f_left_over = str(self.frames_vprs / self.input_fps)[:5]
                    self.m3u8_vprsls.append('#EXTINF:' + self.f_left_over + ',')
                    self.m3u8_vprsls.append(self.called_quality + '-' + str(self.name_counter_vprs) + '.ts')
                    self.m3u8_vprsls.append('#EXT-X-ENDLIST')
                    break
            self.make_m3u8(self.m3u8_vprsls,self.called_quality)

    # m3u8 creator function
    def make_m3u8(self,m3u8_list,c_res):
        self.m3u8_list = m3u8_list
        self.c_res = str(c_res)
        self.str_ = ''
        for self.ls in self.m3u8_list:
            self.str_ += (self.ls + '\n')
        self.m3u8_str = self.str_
        self.m3u8_file = open(r'' + str(self.save_Path) + '/' + self.c_res + '-playlist.m3u8' , 'w')
        self.m3u8_file.write(self.m3u8_str)
        return self.m3u8_file.close()

    # m3u8 Master Creator Function

    def m3u8_master_builder(self,master_list):
        self.master_list = master_list
        self.master_str_ = ''
        for self.list_str in self.master_list:
            self.master_str_ += (self.list_str + '\n')
        self.master_m3u8_file = open(r'' + self.project_path + '/' + self.input_fname + '.m3u8', 'w')
        self.master_m3u8_file.write(self.master_str_)
        return self.master_m3u8_file.close()

    # encode defined qualities
    def encoder(self,resulation):
        self.resulation = str(resulation)
        self.qlist = str(self.q360['height']) + ',' + str(self.q480['height']) + ',' + str(self.q720['height']) + ',' + str(self.q1080['height'])
        self.master_m3u8_list = ['#EXTM3U']
        if '360' in self.resulation:
            self.encode_processor('360',self.q360['width'],self.q360['height'],self.q360['b:v'],self.q360['b:a'])
            self.master_m3u8_list.append('#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=460560,RESULATION=640X360,NAME="360"')
            self.master_m3u8_list.append('trimmed/360-playlist.m3u8')
   
        if '480' in self.resulation:
            self.encode_processor('480',self.q480['width'],self.q480['height'],self.q480['b:v'],self.q480['b:a'])
            self.master_m3u8_list.append('#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=836280,RESULATION=848X480,NAME="480"')
            self.master_m3u8_list.append('trimmed/480-playlist.m3u8')
      
        if '720' in self.resulation:
            self.encode_processor('720',self.q720['width'],self.q720['height'],self.q720['b:v'],self.q720['b:a'])
            self.master_m3u8_list.append('#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=2149280,RESULATION=1280X720,NAME="720"')
            self.master_m3u8_list.append('trimmed/720-playlist.m3u8')
      
        if '1080' in self.resulation:
            self.encode_processor('1080',self.q1080['width'],self.q1080['height'],self.q1080['b:v'],self.q1080['b:a'])
            self.master_m3u8_list.append('#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=6221600,RESULATION=1920X1080,NAME="720"')
            self.master_m3u8_list.append('trimmed/1080-playlist.m3u8')
      
        return self.m3u8_master_builder(self.master_m3u8_list)
