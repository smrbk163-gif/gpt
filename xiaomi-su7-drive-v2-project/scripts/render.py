from pathlib import Path
import json,subprocess,math,os
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent.parent
scenes=json.loads((R/'scenes.json').read_text());inputs={x['name']:x for x in json.loads((R/'inputs.json').read_text())};L='#BFFF00';W='#FFFFFF'
def clamp(x):return max(0.,min(1.,x))
def ease(x):return 1-(1-clamp(x))**4
def font(sz,italic=False):return ImageFont.truetype(str(R/'fonts'/('Montserrat-900-italic.ttf' if italic else 'Montserrat-900-normal.ttf')),sz)
def text(d,s,y,size,color=W,italic=False):
 f=font(size,italic)
 while d.textbbox((0,0),s,font=f)[2]>868:size-=2;f=font(size,italic)
 d.text((540,y),s,font=f,fill=color,anchor='mt')
def path(d,pts,p,color=L,width=4):
 lengths=[math.hypot(b[0]-a[0],b[1]-a[1]) for a,b in zip(pts,pts[1:])];left=sum(lengths)*clamp(p)
 for a,b,le in zip(pts,pts[1:],lengths):
  if left<=0:break
  q=min(1,left/max(le,1e-5));end=(a[0]+(b[0]-a[0])*q,a[1]+(b[1]-a[1])*q);d.line([a,end],fill=color,width=width);left-=le
 return pts[-1]
def overlay(s,t,static):
 base=1160 if s['bottom'] else 105;y=base+395;remaining=s['frames']/60-t;alpha=min(ease(t/.16),clamp(remaining/.14));im=static.copy();d=ImageDraw.Draw(im)
 # Staggered digit reels, with punctuation held in place.
 value=s['value'];size=164 if len(value)<=6 else 100;f=font(size,True);height=202
 if any(c.isdigit() for c in value):
  widths=[int(max(f.getlength('8')+16,50)) if c.isdigit() else int(f.getlength(c)+10) for c in value];x=540-sum(widths)//2
  for i,(c,w) in enumerate(zip(value,widths)):
   if c.isdigit():
    reel=Image.new('RGBA',(w+10,height*4));rd=ImageDraw.Draw(reel)
    for j in range(4):rd.text((w/2+5,j*height),str((int(c)+3-j)%10),font=f,fill=L,anchor='mt')
    q=ease((t-.06-i*.028)/.58);pos=round(q*3*height);patch=reel.crop((0,pos,w+10,pos+height));im.alpha_composite(patch,(x,base+67))
   else:
    if c==',':d.text((x+w/2,base+67+f.getbbox('8',anchor='mt')[3]),c,font=f,fill=L,anchor='ms')
    else:d.text((x+w/2,base+67),c,font=f,fill=L,anchor='mt')
   x+=w
 else:
  temp=Image.new('RGBA',(1080,1920));td=ImageDraw.Draw(temp);text(td,value,base+67+round(65*(1-ease((t-.06)/.38))),size,L,True);im.alpha_composite(temp)
 p=ease((t-.25)/.6);q=ease((t-.15)/.52);kind=s['kind']
 # Art-directed technical frame and fine ticks.
 for j in range(17):
  xx=270+j*34;op=int(30+100*clamp((t-.26-j*.016)/.12));d.line((xx,y+143,xx,y+147+(j%4==0)*8),fill=(255,255,255,op),width=2)
 path(d,[(160,base+20),(115,base+20),(115,base+300),(160,base+300)],q,(191,255,0,150),3)
 path(d,[(920,base+20),(965,base+20),(965,base+300),(920,base+300)],q,(191,255,0,150),3)
 if kind=='power':
  pts=[(250,y+60),(345,y+60),(380,y+28),(410,y+88),(445,y+5),(480,y+96),(520,y+35),(560,y+60),(825,y+60)];path(d,pts,p,L,5)
  for j in range(14):
   h=(10+abs(math.sin(j*.9+t*7))*34)*clamp((t-.45-j*.02)/.12);xx=295+j*37;d.rounded_rectangle((xx,y+125-h,xx+13,y+125),radius=3,fill=(191,255,0,180))
 elif kind in ['accel','speed']:
  if kind=='accel':
   d.line((260,y+110,820,y+110),fill=(255,255,255,70),width=2)
   pts=[(275,y+96),(350,y+94),(440,y+83),(520,y+57),(595,y+22),(700,y+6),(805,y+4)];path(d,pts,p,L,5)
   xx=275+530*p;yy=y+96-92*p*p;d.ellipse((xx-7,yy-7,xx+7,yy+7),fill=W)
  else:
   box=(355,y-10,725,y+205);d.arc(box,185,355,fill=(255,255,255,70),width=4);d.arc(box,185,185+170*p,fill=L,width=6)
   angle=math.radians(185+170*p);cx=540;cy=y+112;ex=cx+155*math.cos(angle);ey=cy+88*math.sin(angle);d.line((cx,cy,ex,ey),fill=W,width=4);d.ellipse((cx-7,cy-7,cx+7,cy+7),fill=L)
 elif kind=='drive':
  path(d,[(365,y+105),(365,y+12),(400,y-10),(680,y-10),(715,y+12),(715,y+105),(365,y+105)],p,W,3)
  for xx in [340,700]:
   d.rounded_rectangle((xx,y+5,xx+42,y+40),radius=9,outline=(255,255,255,80),width=3);d.rounded_rectangle((xx,y+71,xx+42,y+112),radius=9,outline=L,width=4)
  path(d,[(382,y+90),(505,y+90),(540,y+65),(575,y+90),(700,y+90)],p,L,5);d.ellipse((520,y+45,560,y+85),outline=L,width=4)
 elif kind in ['battery','charge']:
  if kind=='battery':
   d.rounded_rectangle((320,y+13,760,y+98),radius=15,outline=W,width=4);d.rectangle((761,y+35,782,y+74),fill=W)
   for j in range(8):
    fill=clamp((t-.32-j*.065)/.15);d.rounded_rectangle((335+j*51,y+27,373+j*51,y+84),radius=4,fill=(191,255,0,int(255*fill)))
   path(d,[(280,y+55),(255,y+55),(240,y+35)],p,L,3);path(d,[(810,y+55),(835,y+55),(850,y+35)],p,L,3)
  else:
   box=(472,y-17,608,y+120);d.arc(box,-90,-90+359*p,fill=L,width=6);d.polygon([(550,y+2),(520,y+55),(546,y+55),(526,y+102),(571,y+42),(544,y+42)],fill=W)
   for j in range(5):
    a=clamp((t-.36-j*.09)/.15);xx=250+j*58;d.line((xx,y+52,xx+28,y+52),fill=(191,255,0,int(210*a)),width=4);xx=680+j*43;d.line((xx,y+52,xx+23,y+52),fill=(191,255,0,int(210*a)),width=4)
 elif kind=='range':
  pts=[(245,y+85),(335,y+85),(415,y+20),(645,y+20),(720,y+85),(835,y+85)];path(d,pts,p,L,5)
  for j,(xx,dy) in enumerate([(245,85),(415,20),(645,20),(835,85)]):
   a=clamp((t-.35-j*.12)/.12);rr=8+4*math.sin(max(0,t-.35)*8+j);d.ellipse((xx-rr,y+dy-rr,xx+rr,y+dy+rr),outline=(255,255,255,int(255*a)),width=3)
 elif kind in ['panel','display']:
  d.rounded_rectangle((345,y+10,735,y+112),radius=14,outline=W,width=3);path(d,[(332,y-5),(345,y-20),(745,y-20),(760,y-5)],p,L,3)
  path(d,[(359,y+98),(720,y+22)],p,L,3)
  for j in range(6):
   xx=370+j*58;d.rounded_rectangle((xx,y+29,xx+33,y+49),radius=4,fill=(191,255,0,int(160*clamp((t-.35-j*.04)/.15))))
 elif kind=='seats':
  path(d,[(420,y+10),(385,y+10),(373,y+30),(387,y+68),(455,y+68),(488,y+91),(420,y+91),(405,y+118)],p,W,4)
  path(d,[(605,y+10),(570,y+10),(558,y+30),(572,y+68),(640,y+68),(673,y+91),(605,y+91),(590,y+118)],p,W,4)
  for j in range(3):
   pts=[(325+j*18+9*math.sin(k*.8+t*6),y+100-k*8) for k in range(11)];path(d,pts,p,L,3)
   for k in range(3):
    yy=y+90-((t*50+k*24+j*6)%75);d.line((690+j*17,yy,690+j*17,yy+10),fill=L,width=3)
 elif kind=='roof':
  path(d,[(315,y+100),(340,y+8),(740,y+8),(765,y+100),(315,y+100)],p,W,4)
  for j in [1,2]:path(d,[(340+j*132,y+8),(340+j*132,y+100)],p,L,3)
  path(d,[(365,y+82),(665,y+27)],p,(191,255,0,180),5)
 elif kind=='mirror':
  d.rounded_rectangle((405,y+5,595,y+90),radius=24,outline=W,width=4);path(d,[(595,y+45),(640,y+70)],p,W,4);d.arc((355,y-22,680,y+147),190,190+115*p,fill=L,width=4)
  # Brief manually aligned frame around the physical mirror.
  if .40<t<1.75:
   a=min(clamp((t-.40)/.14),clamp((1.75-t)/.16));cx=510-32*clamp((t-.4)/1.3);cy=600+30*clamp((t-.4)/1.3)
   for sx,sy in [(-1,-1),(1,-1),(-1,1),(1,1)]:
    xx=cx+sx*245;yy=cy+sy*160;d.line([(xx-sx*60,yy),(xx,yy),(xx,yy-sy*60)],fill=(191,255,0,int(255*a)),width=4)
 elif kind=='light':
  d.rounded_rectangle((350,y+8,510,y+97),radius=26,outline=W,width=4)
  for j in range(5):path(d,[(550,y+12+j*19),(720+(j%2)*50,y+12+j*19)],clamp((t-.30-j*.05)/.35),L,4)
 elif kind=='steering':
  d.arc((425,y-12,655,y+134),0,360*p,fill=W,width=4);path(d,[(435,y+36),(480,y+45),(540,y+40),(600,y+45),(645,y+36)],p,L,4);path(d,[(540,y+45),(540,y+119)],p,W,4)
 elif kind=='end':
  d.ellipse((505,y+4,575,y+75),outline=L,width=4);path(d,[(509,y+65),(540,y+116),(571,y+65)],p,L,4);d.ellipse((529,y+27,551,y+49),fill=W)
 else:
  path(d,[(270,y+36),(810,y+36)],p,L,5)
 # Whole group fades on exit; type remains shadow-free.
 if alpha<1:im.putalpha(im.getchannel('A').point(lambda a:int(a*alpha)))
 return im

def render_one(i):
 s=scenes[i];meta=inputs[s['source']];start=s['sourceStart'];span=s['sourceEnd']-start;dur=s['frames']/60;tr=R/'analysis'/f'transforms-{i}.trf';env={**os.environ,'OMP_NUM_THREADS':'1'}
 common=['ffmpeg','-v','error','-y','-threads','2','-ss',str(start),'-t',str(span),'-i',meta['path']]
 subprocess.run(common+['-map','0:v:0','-an','-filter_threads','1','-vf',f'scale=1080:1920:flags=lanczos,format=yuv420p,vidstabdetect=shakiness=6:accuracy=9:stepsize=12:mincontrast=0.18:result={tr}','-f','null','-'],check=True,env=env)
 k=.20 if span<2.4 else .25
 vf=f"scale=1080:1920:flags=lanczos,format=yuv420p,vidstabtransform=input={tr}:smoothing=22:optalgo=gauss:maxshift=18:maxangle=0.008:zoom=4.5:optzoom=0:interpol=bicubic,format=yuv420p,setpts=PTS-STARTPTS,setpts='{dur}*(T/{span}-{k}*sin(2*PI*T/{span})/(2*PI))/TB',fps=60,tpad=stop_mode=clone:stop_duration=0.1,trim=end_frame={s['frames']},setsar=1"
 decode=subprocess.Popen(common+['-map','0:v:0','-an','-filter_threads','1','-vf',vf,'-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env)
 out=R/'public'/f'scene-{i+1}.mp4';enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','60','-i','pipe:0','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','16','-pix_fmt','yuv420p','-map_metadata','-1','-write_tmcd','0','-movflags','+faststart',str(out)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 base=1160 if s['bottom'] else 105;yy,xx=np.mgrid[0:1920,0:1080];a=np.clip(1-(((xx-540)/690)**2+((yy-(base+255))/500)**2),0,1)**1.6*.78
 rgba=np.zeros((1920,1080,4),dtype=np.uint8);rgba[:,:,3]=(a*255).astype(np.uint8);static=Image.fromarray(rgba);d=ImageDraw.Draw(static);text(d,s['label'],base+12,29);text(d,s['unit'],base+292,30)
 for n in range(s['frames']):
  need=1080*1920*3;parts=[]
  while need:
   b=decode.stdout.read(need)
   if not b:raise RuntimeError(f'Short decode in {i}, frame {n}: '+decode.stderr.read().decode())
   parts.append(b);need-=len(b)
  frame=Image.frombytes('RGB',(1080,1920),b''.join(parts));frame=Image.alpha_composite(frame.convert('RGBA'),overlay(s,n/60,static)).convert('RGB');enc.stdin.write(frame.tobytes())
 enc.stdin.close();ec=enc.wait();er=enc.stderr.read().decode();decode.stdout.close();dc=decode.wait();de=decode.stderr.read().decode()
 if ec or dc:raise RuntimeError(er+de)
 print('ready',i+1,s['kind'],out.stat().st_size,flush=True)
import sys
indices=[int(a)-1 for a in sys.argv[1:]] if len(sys.argv)>1 else list(range(len(scenes)))
with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(render_one,indices))
(R/'concat.txt').write_text(''.join(f"file '{(R/'public'/f'scene-{i+1}.mp4').resolve()}'\n" for i in range(len(scenes))))
