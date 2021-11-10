# 视频转音频
from tqdm import tqdm
from moviepy.editor import *

path = '/home/dango/multimodal/Semi-automatic_labeling/'

for i in tqdm(range(80, 81)):
    video = VideoFileClip(path + 'mp4/' + str(i) + '.mp4')
    audio = video.audio
    audio.write_audiofile(path + 'wav/' + str(i) + '.wav')
    
# 音频分割
import auditok
from tqdm import tqdm

path = '/home/dango/multimodal/Semi-automatic_labeling/'
log_file = path + '001.txt'
with open(log_file, 'w') as log_f:
    log_f.write('Episode|StartTime|EndTime|Utterance|Dialogue|Sentence|Speaker|Sentiment|Emotion\n')

for i in tqdm(range(80, 81)):
    region_main = auditok.core.AudioRegion.load(path + 'wav/' + str(i) + '.wav')
    audio_regions = auditok.core.split(region_main, min_dur=0.8, max_dur=1000, max_silence=0.08, drop_trailing_silence=True)
    for region in audio_regions:
        audiofile = region.save(path + 'split_wav/' + str(i) + '|{meta.start:.2f}|{meta.end:.2f}.wav')
        with open(log_file, 'a') as log_f:
            log_f.write(str(i) + '|%.2f|%.2f\n' %(region.meta.start, region.meta.end))
            
# 分割视频
from tqdm import tqdm
from moviepy.editor import *

path = '/home/dango/multimodal/Semi-automatic_labeling/'
log_file = path + '001.txt'

with open(log_file, 'r') as log_f:
    lines = log_f.readlines()[1:]
    for line in tqdm(lines):
        epi = line.strip().split('|')[0]
        sta = line.strip().split('|')[1]
        end = line.strip().split('|')[2]
        clip = VideoFileClip(path + 'mp4/' + epi + '.mp4').subclip(float(sta), float(end))
        clip.write_videofile(path + 'split_mp4/' + epi + '|' + sta + '|' + end + '.mp4')
        
# 视频截取表情，特征提取

# 表情情感识别

# 语音转写
from tqdm import tqdm
import speech_recognition

r = speech_recognition.Recognizer()
path = '/home/dango/multimodal/Semi-automatic_labeling/'
log_file = path + '001.txt'
another_file = path + '002.txt'
with open(another_file, 'w') as ano_f:
    ano_f.write('Episode|StartTime|EndTime|Utterance|Dialogue|Sentence|Speaker|Sentiment|Emotion\n')

with open(log_file, 'r') as log_f:
    lines = log_f.readlines()[1:]
    for line in tqdm(lines):
        audiofile = path + 'split_wav/' + line.strip() + '.wav'
        with speech_recognition.AudioFile(audiofile) as source:
            audio_1 = r.record(source)
        try:
            sent_1 = r.recognize_google(audio_1, language='zh')
            with open(another_file, 'a') as ano_f:
                ano_f.write(line.strip() + '|' + sent_1 + '\n')
        except:
            with open(another_file, 'a') as ano_f:
                ano_f.write(line.strip() +'|' + '-' + '\n')
                
# 音频特征提取

# 音频情感识别

# 文字特征提取，对比学习

# 文字情感识别

# 半自动标注，标签文件，表情和说话人有没有对上，情感强度

# 多人人工修正
