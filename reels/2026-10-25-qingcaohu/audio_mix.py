import subprocess,sys,numpy as np
S=sys.argv[1]; A=S+'/sfx/a/'; DUR=39.1
def pcm(f):
    raw=subprocess.run(['ffmpeg','-v','error','-i',f,'-ac','1','-ar','8000','-f','s16le','-'],capture_output=True).stdout
    return np.abs(np.frombuffer(raw,np.int16).astype(float))
def onset(f): x=pcm(f); return np.argmax(x>x.max()*0.2)/8000
def peak(f): x=pcm(f); e=np.convolve(x,np.ones(400)/400,'same'); return float(np.argmax(e[:48000]))/8000
# events: (file, timeline_t, align, vol, src_ss, max_len, fade_out)
E=[(S+'/src/210.mp4',0.0,'at',0.9,4.0,1.5,0.15),
   (A+'1092.mp3',1.5,'on',1.0,0,0.9,0.25),
   (A+'1206.mp3',2.6,'at',0.45,10,2.5,0.4)]
E+=[(A+'1430.mp3',t,'on',0.8,0,None,0) for t in (7.1,7.7,8.3,8.9)]
E+=[(A+'2364.mp3',10.3+0.2*i,'on',0.55,0,0.25,0.05) for i in range(11)]
E+=[(A+'2192.mp3',14.0,'on',1.0,0,None,0)]
E+=[(A+'2350.mp3',28.4,'pk',0.8,0,None,0)]
E+=[(S+'/src/210.mp4',29.4,'at',0.75,2.0,9.7,1.5)]
ins=[];fl=[]
for k,(f,t,al,vol,ss,ml,fo) in enumerate(E):
    off={'on':onset,'pk':peak}.get(al,lambda f:0)(f) if al!='at' else 0
    delay=max(0,t-off); ss2=ss+max(0,off-t)
    ins+=['-ss',str(ss2)]+(['-t',str(ml)] if ml else [])+['-i',f]
    chain=f'[{k}:a]aresample=48000,aformat=channel_layouts=stereo,volume={vol}'
    if fo and ml: chain+=f',afade=t=out:st={ml-fo}:d={fo}'
    chain+=f',adelay={int(delay*1000)}:all=1[e{k}]'; fl.append(chain)
n=len(E); m=n
ins+=['-ss','24.5','-i',S+'/music/839.mp3']
fl.append(''.join(f'[e{k}]' for k in range(n))+f'amix=inputs={n}:normalize=0,apad,atrim=0:{DUR},asplit[sfx][key]')
fl.append(f'[{m}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{DUR-2.0},asetpts=PTS-STARTPTS,volume=0.55,afade=t=in:d=0.5,afade=t=out:st={DUR-2.0-2.2}:d=2.2,adelay=2000:all=1,apad,atrim=0:{DUR}[mus]')
fl.append('[mus][key]sidechaincompress=threshold=0.03:ratio=5:attack=15:release=300:makeup=1[duck]')
fl.append('[duck][sfx]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[out]')
subprocess.run(['ffmpeg','-v','error','-y',*ins,'-filter_complex',';'.join(fl),'-map','[out]','-c:a','pcm_s16le',S+'/final_mix.wav'],check=True)
