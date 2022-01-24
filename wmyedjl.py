# 这个部分是按照字幕，手工分割+标注是否有正脸+正负极情感
import os

seq = 988 # 接下来要开始的序号
episode = 10  # 第几集

srt = '../multimodal_dataset/srt/' + str(episode) + '.srt'
with open(srt, 'r') as srt_f:
    lines = srt_f.readlines()
add = [0.00, 6.14, 6.10, 6.16, 6.11, 6.11, 6.15, 6.08, 6.13, 5.70, 5.91]
count = seq-1
utterance = ''
time_list = []
while count < len(lines)-3:
    if lines[count].strip() == str(seq):
        mod = input('更新对话输入1：')
        if mod == '1':
            conversation = input('第几段对话就填几：')
            sentence = input('第几句话就填几：')
        file_name = '../multimodal_dataset/split_log/'+str(episode)+'_'+conversation+'_'+sentence+'.txt'
        
        switch = input('截断对话输入1：'+utterance+lines[count+2].strip())
        utterance = utterance + lines[count+2].strip() + ' '
        if lines[count+3].strip() != '':
            switch = input('截断对话输入1：'+utterance+lines[count+3].strip())
            utterance = utterance + lines[count+3].strip() + ' '
        
        time = lines[count+1].strip().split(' --> ')
        for i in range(2):
            hour, minute, second, ms = float(time[i].split(':')[0]), float(time[i].split(':')[1]), float(time[i].split(':')[2].split(',')[0]), float(time[i].split(':')[2].split(',')[1])
            time_list.append(str(3600*hour + 60*minute + second + ms/1000 - add[int(episode)]))
        
        if switch == '1':
            utterance = utterance[:-1]
            speaker = input('第几个人说的就填几：')
            face = input('有正脸填1，没有填0：')
            emotion = input('情感强度-3~3：')
            start_time = time_list[0]
            end_time = time_list[-1]
            if os.path.exists(file_name) == False:
                with open(file_name, 'w') as log_f:
                    log_f.write(str(episode)+'|'+start_time+'|'+end_time+'|'+utterance+'|'+conversation+'|'+sentence+'|'+speaker+'|'+face+'|'+emotion+'| ')
            else:
                print('！！！文件重复！！！')
            utterance = ''
            time_list = []
            sentence = str(int(sentence)+1)
        seq += 1
    count += 1
# 3  有夸张的正面情绪表情
# 2  有正面情绪表情
# 1  情绪不明显偏正面
# 0  情绪中立
# -1 情绪不明显偏负面
# -2 有负面情绪表情
# -3 有夸张的负面情绪表情
#################################################

# 这个部分按照字幕中时间间隔和分割时长，自动重新分割（粗略标注）
import os
from tqdm import tqdm

episode = 10
add = [0.00, 6.14, 6.10, 6.16, 6.11, 6.11, 6.15, 6.08, 6.13, 5.70, 5.91]

srt_file = '../multimodal_dataset/srt/'+str(episode)+'.srt'
with open(srt_file, 'r') as srt_f:
    lines = srt_f.readlines()

conv, fake_sent, sent, count = 1, 1, 1, -2

while count < len(lines)-1:

    log_file = '../multimodal_dataset/split_log/'+str(episode)+'_'+str(conv)+'_'+str(fake_sent)+'.txt'
    if os.path.exists(log_file) == False:
        if fake_sent == 1:
            break
        else:
            conv += 1
            fake_sent, sent = 1, 1
            log_file = '../multimodal_dataset/split_log/'+str(episode)+'_'+str(conv)+'_'+str(fake_sent)+'.txt'

    with open(log_file, 'r') as log_f:
        line = log_f.readlines()[0].split('|')
        speaker, face, sentiment = line[6], line[7], line[8]
        text_content = line[3]

    # 第一次分割
    text_list, start_list, jiange_list, end_list, chixu_list = [], [], [], [], []
    end_time = 0
    while 1:
        count += 4
        temp_text = lines[count].strip()
        time = lines[count-1].strip().split(' --> ')
        if lines[count+1].strip() != '':
            temp_text = temp_text + ' ' + lines[count+1].strip()
            count += 1
        if temp_text in text_content:
            text_list.append(temp_text)
            hour, minute, second, ms = float(time[0].split(':')[0]), float(time[0].split(':')[1]), float(time[0].split(':')[2].split(',')[0]), float(time[0].split(':')[2].split(',')[1])
            start_time = 3600*hour + 60*minute + second + ms/1000 - add[int(episode)]
            start_list.append(str(start_time))
            if end_time == 0:
                end_time = start_time
            jiange_time = start_time - end_time
            jiange_list.append(jiange_time)
            hour, minute, second, ms = float(time[1].split(':')[0]), float(time[1].split(':')[1]), float(time[1].split(':')[2].split(',')[0]), float(time[1].split(':')[2].split(',')[1])
            end_time = 3600*hour + 60*minute + second + ms/1000 - add[int(episode)]
            end_list.append(str(end_time))
            chixu_time = end_time - start_time
            chixu_list.append(chixu_time)
            if temp_text == text_content[-len(temp_text):]:
                break

    # 按间隔时间分割
    if len(text_list) > 1:
        num = 0
        temp_list = []
        for i in range(len(jiange_list)):
            if jiange_list[i] > 0.5:
                temp_list.append(chixu_list[num:i])
                num = i
        temp_list.append(chixu_list[num:])

        list_da = []
        for temp in temp_list:
            list_xiao = []
            num = 0
            for chixu_time in temp:
                list_xiao.append(chixu_time)
                num += 1
                if sum(list_xiao) > 2.0 and num < len(temp)-1 and sum(temp[num:]) > 2.0:
                    list_da.append(list_xiao)
                    list_xiao = []
            list_da.append(list_xiao)

        # 写日志
        start, end = 0, 0
        for da in list_da:
            start, end = end, end+len(da)
            text = ' '.join(text_list[start:end])
            start_time = start_list[start]
            end_time = end_list[end-1]
            file_name = '../multimodal_dataset/temp_log/'+str(episode)+'_'+str(conv)+'_'+str(sent)+'.txt'
            if os.path.exists(file_name) == False:
                with open(file_name, 'w') as file:
                    file.write(str(episode)+'|'+str(conv)+'|'+str(sent)+'|'+start_time+'|'+end_time+'|'+text+'|'+speaker+'|'+face+'|'+sentiment+'\n')
                    sent += 1
            else:
                print('文件重复！！！')

    else:
        file_name = '../multimodal_dataset/temp_log/'+str(episode)+'_'+str(conv)+'_'+str(sent)+'.txt'
        if os.path.exists(file_name) == False:
            with open(file_name, 'w') as file:
                file.write(str(episode)+'|'+str(conv)+'|'+str(sent)+'|'+start_list[0]+'|'+end_list[0]+'|'+text_list[0]+'|'+speaker+'|'+face+'|'+sentiment+'\n')
                sent += 1
        else:
            print('！！！文件重复')
    fake_sent += 1
#########################################################

# 这个部分是按粗略标注的结果，分割音频和视频                      
import os
from moviepy.editor import *
from pydub import AudioSegment

epi = 6
con = 1
sen = 1
path = '../multimodal_dataset/'
wav = AudioSegment.from_wav(path + 'wav/' + str(epi) + '.wav')

while 1:
    # 读取 file
    file = path + 'temp_log/'+str(epi)+'_'+str(con)+'_'+str(sen)+'.txt'
    if os.path.exists(file) == False:
        con += 1
        sen = 1
        continue
    with open(file, 'r') as log_f:
        line = log_f.readlines()[0].strip()
    start = float(line.split('|')[3])
    end = float(line.split('|')[4]) 
    wav[start*1000:end*1000].export(path+'split_wav/'+str(epi)+'_'+str(con)+'_'+str(sen)+'.wav', format="wav")
    clip = VideoFileClip(path + 'mkv/' + str(epi) + '.mkv').subclip(start, end)
    clip.write_videofile(path + 'split_mkv/'+str(epi)+'_'+str(con)+'_'+str(sen)+'.mp4', codec="libx264")
    sen += 1
    
###############################################

# 这个部分是手工标注8+1种情感（精细标注）
import os

epi = 1  # 第几集
con = 1  # 第几段对话
sen = 3  # 第几句话

while 1:
    file = '../multimodal_dataset/temp_log/'+str(epi)+'_'+str(con)+'_'+str(sen)+'.txt'  # 读取文件地址
    if os.path.exists(file) == False:
        con += 1
        sen = 1
        continue
    with open(file, 'r') as log_f:
        line = log_f.readlines()[0].strip()
    fen = int(float(line.split('|')[3]) // 60)
    miao = int(float(line.split('|')[3]) - fen * 60)
    fen, miao = str(fen), str(miao)
    if len(fen) == 1:
        fen = '0' + fen
    if len(miao) == 1:
        miao = '0' + miao
    
    # 标注 情感强度
    print('开始时间：'+fen+':'+miao)
    print('对话内容：'+line.split('|')[5])
    joy = input('（积极）高兴/快乐 的程度：')
    joy = min(3, int(joy))
    exp = input('（积极）期待/期盼 的程度：')
    exp = min(3, int(exp))
    sur = input('（积极）吃惊/惊讶 的程度：')
    sur = min(3, int(sur))
    lov = input('（积极）喜爱/喜欢 的程度：')
    lov = min(3, int(lov))
    sor = input('（消极）悲伤/伤心 的程度：')
    sor = min(3, int(sor))
    ang = input('（消极）愤怒/生气 的程度：')
    ang = min(3, int(ang))
    anx = input('（消极）焦虑/忧愁 的程度：')
    anx = min(3, int(anx))
    hat = input('（消极）怨恨/讨厌 的程度：')
    hat = min(3, int(hat))
    
    
    # 修正 sentiment
    zheng = max(joy,exp,sur,lov)
    fu = max(sor,ang,anx,hat)
    neu = str(0)
    if zheng == 0 and fu == 0:
        sentiment = str(0)
        neu = str(1)
    elif zheng == 0 and fu > 0:
        sentiment = str(fu)
    elif zheng > 0 and fu == 0:
        sentiment = str(zheng)
    else:
        sentiment = line.split('|')[-1]
    
    log_file = '../multimodal_dataset/name_log/'+str(epi)+'_'+str(con)+'_'+str(sen)+'.txt'  # 写入文件地址
    with open(log_file, 'w') as log_f:
        log_f.write('Episode|Dialogue|Sentence|StartTime|EndTime|Utterance|Speaker|Face|Sentiment|Love|Anxiety|Sorrow|Joy|Expect|Hate|Anger|Surprise|Neutral\n')
    still_list = line.split('|')[:]
    still = still_list[0]+'|'+still_list[1]+'|'+still_list[2]+'|'+str(round(float(still_list[3]),3))+'|'+str(round(float(still_list[4]),3))+'|'+still_list[5]
    still = still+'|'+still_list[6]+'|'+still_list[7]+'|'+sentiment+'|'+str(lov)+'|'+str(anx)+'|'+str(sor)+'|'+str(joy)+'|'+str(exp)+'|'+str(hat)+'|'+str(ang)+'|'+str(sur)+'|'+neu+'\n'
    with open(log_file, 'a') as log_f:
        log_f.write(still)
    sen += 1
    
# 3  有夸张的情绪表情
# 2  有情绪表情
# 1  情绪表情不明显
# 0  无情绪表情
