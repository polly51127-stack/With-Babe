# Renders animated caption/decoration overlay as raw RGBA frames to stdout
import sys,math,os
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageChops
W,H,FPS,DUR=1080,1920,30,39.1
FONT=os.path.expanduser('~/.fonts/NotoSerifCJKtc-Black.otf')
font=ImageFont.truetype(FONT,72)
# text, start, end, y-center fraction, anim
CAPS=[('跟你看這場煙火之前...',0,1.5,0.45,'type'),
('回到早上 10 點',1.5,2.6,0.22,'pop'),
('新竹的海風很大',2.6,5.1,0.12,'rise'),
('我男友拍照的時候',9.5,13.8,0.14,'rise'),
('但還是很可愛啦',13.8,15.2,0.12,'rise'),
('先去吃海鮮',15.2,17.7,0.22,'rise'),
('動物園巡禮',17.7,20.0,0.12,'rise'),
('出發！青草湖',20.0,21.0,0.70,'pop'),
('青草湖 × 蠟筆小新',21.0,23.6,0.12,'rise'),
('一起等天黑',23.6,25.6,0.72,'rise'),
('謝謝你陪我看這場煙火',29.4,36.9,0.25,'type')]
PAD=40
def sprite(txt,fnt=font,fill=(255,255,255,255)):
    l,t,r,b=fnt.getbbox(txt); w,h=r-l+2*PAD,b-t+2*PAD
    a=Image.new('L',(w,h),0); ImageDraw.Draw(a).text((PAD-l,PAD-t),txt,font=fnt,fill=255)
    g=ImageChops.add(a.filter(ImageFilter.GaussianBlur(14)).point(lambda v:min(255,int(v*2.2))),
                     a.filter(ImageFilter.GaussianBlur(5)).point(lambda v:min(255,int(v*1.6))))
    im=Image.new('RGBA',(w,h),(0,0,0,0)); im.putalpha(g)
    fg=Image.new('RGBA',(w,h),fill); fg.putalpha(a); im.alpha_composite(fg)
    return im,(PAD-l,PAD-t)
cache={}
def get(txt):
    if txt not in cache: cache[txt]=sprite(txt)
    return cache[txt]
def ease(x): x=max(0,min(1,x)); return 1-(1-x)**3
def back(x):
    x=max(0,min(1,x)); c=1.70158; return 1+(c+1)*(x-1)**3+c*(x-1)**2
def put(frame,im,cx,cy,alpha=1,scale=1):
    if alpha<=0: return
    if scale!=1: im=im.resize((max(1,int(im.width*scale)),max(1,int(im.height*scale))),Image.BICUBIC)
    if alpha<1: im=im.copy(); im.putalpha(im.getchannel('A').point(lambda v:int(v*alpha)))
    frame.alpha_composite(im,(int(cx-im.width/2),int(cy-im.height/2)))
def heart(sz,color):
    s=4; im=Image.new('RGBA',(sz*s,sz*s),(0,0,0,0)); d=ImageDraw.Draw(im)
    pts=[];
    for k in range(200):
        t=2*math.pi*k/200; x=16*math.sin(t)**3; y=13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t)
        pts.append((sz*s/2+x*sz*s/36,sz*s/2-y*sz*s/36))
    d.polygon(pts,fill=color); im=im.resize((sz,sz),Image.LANCZOS)
    g=Image.new('RGBA',(sz+40,sz+40),(0,0,0,0)); sh=Image.new('RGBA',(sz+40,sz+40),(0,0,0,0)); sh.paste(im,(20,20))
    a=sh.getchannel('A').filter(ImageFilter.GaussianBlur(8)).point(lambda v:int(v*0.6)); g.putalpha(a); g.alpha_composite(sh); return g
def star(sz):
    s=4; R=sz*s/2; im=Image.new('RGBA',(sz*s,sz*s),(0,0,0,0)); d=ImageDraw.Draw(im); pts=[]
    for k in range(8):
        r=R if k%2==0 else R*0.22; a=math.pi/4*k-math.pi/2; pts.append((R+r*math.cos(a),R+r*math.sin(a)))
    d.polygon(pts,fill=(255,250,220,255)); im=im.resize((sz,sz),Image.LANCZOS)
    g=Image.new('RGBA',(sz+40,sz+40),(0,0,0,0)); sh=Image.new('RGBA',(sz+40,sz+40),(0,0,0,0)); sh.paste(im,(20,20))
    a=sh.getchannel('A').filter(ImageFilter.GaussianBlur(6)); g=Image.new('RGBA',sh.size,(255,240,180,0)); g.putalpha(a); g.alpha_composite(sh); return g
HEART=heart(70,(255,92,138,255)); HEART2=heart(46,(255,140,170,255)); STAR=star(60)
ARROW=get('↓')
out=sys.stdout.buffer
for fi in range(round(DUR*FPS)):
    t=fi/FPS; fr=Image.new('RGBA',(W,H),(0,0,0,0))
    for (txt,a,b,yf,an) in CAPS:
        if not(a<=t<b): continue
        lt=t-a; cy=yf*H; out_a=min(1,(b-t)/0.2) if b<DUR-0.01 else 1
        if an=='type':
            n=len(txt); per=0.07 if b-a<3 else 0.11
            k=min(n,int(lt/per)+1); im,_=get(txt[:k]); full,_=get(txt)
            # left-align with full string's centered position
            x0=W/2-full.width/2; put(fr,im,x0+im.width/2,cy,out_a)
        elif an=='pop':
            im,_=get(txt); p=lt/0.3; put(fr,im,W/2,cy,min(1,p*2)*out_a,0.6+0.4*back(p))
        elif an=='fade':
            im,_=get(txt); put(fr,im,W/2,cy,ease(lt/0.6),1)
        else:
            im,_=get(txt); p=ease(lt/0.35); put(fr,im,W/2,cy+40*(1-p),p*out_a,0.94+0.06*p)
        if txt=='我男友拍照的時候':
            im,_=get(txt); ax=W/2+im.width/2+10; p=ease(lt/0.35)
            put(fr,ARROW[0],ax,cy+12+40*(1-p)+14*abs(math.sin(lt*2*math.pi*1.6)),p*out_a)
    # floating hearts at kiss (13.8-15.2)
    if 13.85<=t<15.2:
        for (x0,d0,hm,sp) in [(0.80,0.0,HEART,1.0),(0.90,0.25,HEART2,1.2),(0.70,0.45,HEART2,0.9)]:
            lt=t-13.85-d0
            if lt<0: continue
            al=min(1,lt/0.15)*max(0,min(1,(1.3-lt)/0.3)); sc=0.5+0.5*back(lt/0.3)
            put(fr,hm,x0*W+18*math.sin(lt*6),0.30*H-160*lt*sp,al,sc)
    # twinkling stars around the moon (28.4-29.4)
    if 28.4<=t<29.4:
        for (x,y,d0,s) in [(0.30,0.38,0.0,1.0),(0.72,0.33,0.15,0.7),(0.62,0.62,0.3,0.85),(0.25,0.60,0.45,0.6),(0.80,0.50,0.2,0.5)]:
            lt=t-28.4-d0
            if lt<0: continue
            put(fr,STAR,x*W,y*H,max(0,math.sin(min(1,lt/0.6)*math.pi)),s*(0.6+0.4*math.sin(min(1,lt/0.6)*math.pi)))
    out.write(fr.tobytes())
