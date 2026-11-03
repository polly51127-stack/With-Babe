import subprocess,sys,os
S=sys.argv[1]; src=S+'/src/'; seg=S+'/seg/'; os.makedirs(seg,exist_ok=True)
FONT='/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
# (type, id, start, dur, text, opts)
P=[('v',208,19.5,1.5,'跟你看這場煙火之前⋯',{}),
   ('rev',208,19.5,1.5,'⏪ 回到早上 10 點',{}),
   ('p',1,0,0.6,'回到早上 10 點',{}),
   ('v',8,0,2.5,'新竹的海風很大',{}),
   ('v',99,0,2.0,'',{}),
   ('p',18,0,0.6,'',{}),('p',21,0,0.6,'',{}),('p',24,0,0.6,'',{}),('p',27,0,0.6,'',{}),
   ('p',47,0,0.8,'我男友拍照的時候 ↓',{'still':1}),
   ('p',52,0,0.2,'@',{'still':1}),('p',56,0,0.2,'@',{'still':1}),('p',60,0,0.2,'@',{'still':1}),
   ('p',63,0,0.2,'@',{'still':1}),('p',66,0,0.2,'@',{'still':1}),
   ('p',52,0,0.2,'@',{'still':1}),('p',56,0,0.2,'@',{'still':1}),('p',60,0,0.2,'@',{'still':1}),
   ('p',63,0,0.2,'@',{'still':1}),('p',66,0,0.2,'@',{'still':1}),
   ('v',67,0,1.5,'@',{}),
   ('p',90,0,1.4,'但還是很可愛啦',{}),
   ('v',98,0,1.5,'先去吃海鮮',{}),('p',103,0,1.0,'@',{}),
   ('v',118,9,1.5,'動物園巡禮',{}),('p',153,0,0.8,'@',{}),
   ('p',166,0,1.0,'出發！青草湖',{}),
   ('p',172,0,0.8,'青草湖 × 蠟筆小新',{}),('p',177,0,0.8,'@',{}),('p',187,0,1.0,'@',{}),
   ('p',193,0,1.0,'一起等天黑',{}),('p',201,0,1.0,'@',{}),
   ('p',198,0,0.8,'',{}),('v',203,0,2.0,'',{}),
   ('p',205,0,1.0,'',{}),
   ('v',208,25,2.0,'謝謝你陪我看這場煙火',{}),('v',207,50,2.0,'@',{}),
   ('v',207,35,2.0,'@',{}),('v',208,30,1.5,'@',{}),
   ('p',218,0,2.2,'2026.10.25 新竹青草湖',{'end':1}),
]
from PIL import Image
OUT='scale=1080:1920,setsar=1,fps=30,format=yuv420p'
def run(c): subprocess.run(c,check=True)
files=[]
for i,(t,n,ss,d,txt,o) in enumerate(P):
    f=seg+'%02d.mp4'%i; files.append(f)
    fr=round(d*30)
    if t in('v','rev'):
        inp=src+'%03d.mp4'%n
        import json
        w,h=map(int,subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height:stream_side_data=rotation','-of','csv=p=0',inp],capture_output=True,text=True).stdout.split('\n')[0].split(',')[:2])
        land = (n in (207,210))
        vf=('crop=ih*9/16:ih,' if land else 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,')+OUT
        if t=='rev': vf+=',reverse,setpts=PTS/3'; fr=round(d*30/3)
        run(['ffmpeg','-v','error','-y','-ss',str(ss),'-t',str(d),'-i',inp,'-vf',vf,'-frames:v',str(fr),'-an','-c:v','libx264','-crf','18','-preset','fast',f])
        P[i]=(t,n,ss,fr/30,txt,o)
    else:
        inp=src+'%03d.jpg'%n; w,h=Image.open(inp).size
        if w>h:  # landscape: blurred background
            vf=f"split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:5,eq=brightness=-0.08[bg];[b]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,"
        else:
            vf="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        if o.get('still'):
            vf+=OUT
        else:
            vf=vf.replace('1080:1920','2160:3840').replace('1080:-2','2160:-2').replace('boxblur=30','boxblur=60')
            vf+=f"zoompan=z='1+0.06*on/{fr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={fr}:s=1080x1920:fps=30,"+OUT
        if o.get('end'): vf+=f',fade=t=out:st={d-0.8}:d=0.8'
        run(['ffmpeg','-v','error','-y','-loop','1','-i',inp,'-filter_complex' if w>h else '-vf',vf,'-frames:v',str(fr),'-c:v','libx264','-crf','18','-preset','fast',f])
        P[i]=(t,n,ss,fr/30,txt,o)
open(seg+'list.txt','w').write(''.join("file '%s'\n"%f for f in files))
# text timeline: '@' = continue previous caption
caps=[];t0=0
for (t,n,ss,d,txt,o) in P:
    if txt=='@': caps[-1][2]=t0+d
    elif txt: caps.append([txt,t0,t0+d])
    t0+=d
print('total',round(t0,2))
dt=[]
for k,(txt,a,b) in enumerate(caps):
    tf=S+'/cap%02d.txt'%k; open(tf,'w').write(txt.replace('⏪ ','').replace('⋯','...'))
    dt.append(f"drawtext=fontfile={FONT}:textfile={tf}:fontsize=68:fontcolor=white:borderw=5:bordercolor=black@0.75:shadowx=0:shadowy=4:shadowcolor=black@0.4:x=(w-text_w)/2:y=h*0.22:enable='between(t,{a:.3f},{b-0.01:.3f})'")
base=S+'/base.mp4'
run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',seg+'list.txt','-c','copy',base])
for name,vf in (('rough_cut_with_text.mp4',','.join(dt)),('rough_cut_no_text.mp4','null')):
    run(['ffmpeg','-v','error','-y','-i',base,'-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-vf',vf,'-shortest','-c:v','libx264','-crf','19','-preset','medium','-profile:v','high','-pix_fmt','yuv420p','-movflags','+faststart','-c:a','aac','-b:a','128k',S+'/'+name])
for c in caps: print(c)
