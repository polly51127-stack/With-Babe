import subprocess,sys,glob
S=sys.argv[1]; font=sys.argv[2]; out=sys.argv[3]
caps=[('跟你看這場煙火之前...',0,1.5),('回到早上 10 點',1.5,2.6),('新竹的海風很大',2.6,5.1),('我男友拍照的時候 ↓',9.5,13.8),
('但還是很可愛啦',13.8,15.2),('先去吃海鮮',15.2,17.7),('動物園巡禮',17.7,20.0),('出發！青草湖',20.0,21.0),
('青草湖 × 蠟筆小新',21.0,23.6),('一起等天黑',23.6,25.6),('謝謝你陪我看這場煙火',29.4,36.9),('2026.10.25 新竹青草湖',36.9,39.1)]
def dt(color,i,txt,a,b):
    tf=f'{S}/cap{i:02d}.txt'; open(tf,'w').write(txt)
    return f"drawtext=fontfile={font}:textfile={tf}:fontsize=72:fontcolor={color}:x=(w-text_w)/2:y=h*0.22:enable='between(t,{a},{b-0.01})'"
glow=','.join(dt('black',i,*c) for i,c in enumerate(caps))
white=','.join(dt('white',i,*c) for i,c in enumerate(caps))
fc=(f"color=c=black@0:s=1080x1920:r=30:d=39.1,format=rgba,{glow},split[g1][g2];"
    f"[g1]gblur=sigma=14[b1];[g2]gblur=sigma=5[b2];[b1][b2]overlay,colorchannelmixer=aa=1.6[glow];"
    f"[0:v][glow]overlay=format=auto,{white}[v]")
subprocess.run(['ffmpeg','-v','error','-y','-i',S+'/base.mp4','-filter_complex',fc,'-map','[v]','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p','-movflags','+faststart',out],check=True)
