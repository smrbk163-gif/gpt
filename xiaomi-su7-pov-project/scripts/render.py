from pathlib import Path
import json,math,subprocess,os
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent.parent;FILES=json.loads((R/'inputs.json').read_text());FRAMES={1:1727,2:1717};L='#BFFF00';W='#FFFFFF'
def clamp(x):return min(1.,max(0.,x))
def ease(x):return 1-(1-clamp(x))**3
@lru_cache(100)
def font(n,italic=False):return ImageFont.truetype(str(R/'fonts'/('Montserrat-900-italic.ttf' if italic else 'Montserrat-900-normal.ttf')),n)
def fitted(text,n,width,italic=False):
 f=font(n,italic)
 while f.getlength(text)>width:n-=1;f=font(n,italic)
 return f
@lru_cache(500)
def word_sprite(word):
 word=word.upper();f=fitted(word,96,850,True);box=f.getbbox(word);w=math.ceil(f.getlength(word))+60;h=175
 im=Image.new('RGBA',(w,h));d=ImageDraw.Draw(im);col=L if word in ['XIAOMI','SU7','ПАНОРАМА','САМАРЕ'] else W;d.text((w/2,20),word,font=f,anchor='mt',fill=col)
 yy,xx=np.mgrid[0:h,0:w];a=np.clip(1-(((xx-w/2)/(w*.63))**2+((yy-70)/100)**2),0,1)**1.7*.63
 rgba=np.zeros((h,w,4),np.uint8);rgba[:,:,3]=(a*255).astype(np.uint8);bg=Image.fromarray(rgba);return Image.alpha_composite(bg,im)
def path(d,points,p,fill,width=2):
 lens=[math.dist(a,b) for a,b in zip(points,points[1:])];left=sum(lens)*clamp(p)
 for a,b,le in zip(points,points[1:],lens):
  if left<=0:break
  q=min(1,left/max(le,1e-6));d.line([a,(a[0]+q*(b[0]-a[0]),a[1]+q*(b[1]-a[1]))],fill=fill,width=width);left-=le

def card_layer(c,t,source):
 local=t-c['start'];remaining=c['end']-t;a=min(ease(local/.18),clamp(remaining/.16));p=ease((local-.04)/.36)
 x=c['x']+round(14*(1-ease(local/.3)));y=c['y'];im=Image.new('RGBA',(1080,1920));d=ImageDraw.Draw(im);cw=440;ch=210
 # Fine anchored callouts only for the visible object, not false measurements.
 if c['kind'] in ['car','screen','roof','seats']:
  if c['kind']=='car':target=(580+20*clamp((t-1.85)/1.5),870+85*clamp((t-1.85)/1.5))
  elif c['kind']=='screen':target=(450-45*clamp(t/2.7),490+35*clamp(t/2.7))
  elif c['kind']=='roof':target=(570,610)
  else:target=(730,1320)
  ax=x+cw/2;ay=y+ch;path(d,[(ax,ay),(ax,ay+36),target],p,(191,255,0,145),2)
  if p>.8:
   rr=8+2*math.sin(local*9);d.ellipse((target[0]-rr,target[1]-rr,target[0]+rr,target[1]+rr),outline=(191,255,0,170),width=2)
 d.rounded_rectangle((x,y,x+cw,y+ch),radius=16,fill=(5,15,15,157),outline=(230,255,246,52),width=1)
 for points in [[(x+32,y),(x,y),(x,y+32)],[(x+cw-32,y+ch),(x+cw,y+ch),(x+cw,y+ch-32)]]:path(d,points,p,(191,255,0,225),3)
 d.text((x+22,y+19),c['label'],font=fitted(c['label'],21,365),fill=(225,245,237,225))
 d.ellipse((x+cw-30,y+22,x+cw-22,y+30),fill=(191,255,0,int(110+100*math.sin(local*4)**2)))
 value=c['value'];f=fitted(value,52,395,True);vy=y+59
 # Small odometer reels for numeric facts; all other labels slide softly.
 if value[0].isdigit() or value.startswith('До '):
  h=78;widths=[round(f.getlength('8')+7) if z.isdigit() else round(f.getlength(z)+4) for z in value];xx=x+22
  for j,(z,w) in enumerate(zip(value,widths)):
   if z.isdigit():
    reel=Image.new('RGBA',(w+8,h*3));rd=ImageDraw.Draw(reel)
    for row in range(3):rd.text((w/2+4,row*h),str((int(z)+2-row)%10),font=f,anchor='mt',fill=L)
    pos=round(ease((local-.08-j*.018)/.4)*h*2);im.alpha_composite(reel.crop((0,pos,w+8,pos+h)),(xx,vy))
   elif z==',':d.text((xx+w/2,vy+f.getbbox('8',anchor='mt')[3]),z,font=f,anchor='ms',fill=L)
   else:d.text((xx+w/2,vy),z,font=f,anchor='mt',fill=L)
   xx+=w
 else:d.text((x+22,vy+round(12*(1-ease((local-.06)/.24)))),value,font=f,fill=L)
 if c['note']:d.text((x+22,y+128),c['note'],font=fitted(c['note'],24,397),fill=W)
 d.line((x+22,y+185,x+cw-22,y+185),fill=(255,255,255,37),width=1);d.line((x+22,y+185,x+22+(cw-44)*p,y+185),fill=(191,255,0,170),width=2)
 # Quiet scan cue: four short corner marks, no fabricated confidence/telemetry.
 if c['kind']=='roof':
  for xx,yy,sx,sy in [(260,450,1,1),(820,450,-1,1),(260,780,1,-1),(820,780,-1,-1)]:path(d,[(xx+sx*28,yy),(xx,yy),(xx,yy+sy*28)],p,(191,255,0,100),2)
 if a<1:im.putalpha(im.getchannel('A').point(lambda v:int(v*a)))
 return im

def graphics(t,source,words,cards):
 im=Image.new('RGBA',(1080,1920));d=ImageDraw.Draw(im)
 # Minimal glasses-style viewport corners.
 for x,y,sx,sy in [(38,90,1,1),(1042,90,-1,1),(38,1810,1,-1),(1042,1810,-1,-1)]:d.line([(x+sx*20,y),(x,y),(x,y+sy*20)],fill=(230,255,248,40),width=1)
 if source==2 and .15<t<2.7:
  op=min(ease((t-.15)/.3),clamp((2.7-t)/.25));d.text((540,102),'ОТ ПЕРВОГО ЛИЦА',font=font(21),anchor='mt',fill=(235,255,248,int(160*op)))
 for c in cards:
  if c['start']<=t<c['end']:im.alpha_composite(card_layer(c,t,source))
 active=[w for w in words if w['startMs']<=t*1000<w['endMs']]
 if len(active)>1:raise RuntimeError('More than one caption word')
 if active:
  w=active[0];age=t-w['startMs']/1000;dur=(w['endMs']-w['startMs'])/1000;remain=w['endMs']/1000-t
  enter=min(.085,dur*.27);leave=min(.065,dur*.23);op=min(ease(age/max(.001,enter)),clamp(remain/max(.001,leave)))
  sprite=word_sprite(w['text']).copy();scale=1+.026*(1-ease(age/max(.001,enter)));sprite=sprite.resize((round(sprite.width*scale),round(sprite.height*scale)),Image.Resampling.LANCZOS)
  sprite.putalpha(sprite.getchannel('A').point(lambda v:int(v*op)))
  in_offset=14*(1-ease(age/max(.001,enter)))
  out_offset=7*(1-clamp(remain/max(.001,leave)))
  dy=round(in_offset-out_offset)
  im.alpha_composite(sprite,((1080-sprite.width)//2,1515+dy))
 return im

def render(source):
 index=source-1;nframes=FRAMES[source];words=json.loads((R/f'captions-source-{source}.json').read_text());cards=json.loads((R/f'cards-source-{source}.json').read_text());tr=R/'analysis'/f'transforms-{source}.trf'
 vf=f'format=yuv420p,vidstabtransform=input={tr}:smoothing=15:optalgo=gauss:maxshift=8:maxangle=0:zoom=2.4:optzoom=0:interpol=bilinear,format=yuv420p,eq=gamma=1.025:saturation=1.01,fps=60,tpad=stop_mode=clone:stop_duration=0.1,trim=end_frame={nframes},setsar=1'
 dec=subprocess.Popen(['ffmpeg','-v','error','-threads','2','-i',FILES[index],'-map','0:v:0','-an','-filter_threads','1','-vf',vf,'-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,env={**os.environ,'OMP_NUM_THREADS':'1'})
 out=R/'public'/f'part-source-{source}.mp4';enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','60','-i','pipe:0','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','16','-pix_fmt','yuv420p','-map_metadata','-1','-write_tmcd','0','-movflags','+faststart',str(out)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 for n in range(nframes):
  need=1080*1920*3;parts=[]
  while need:
   chunk=dec.stdout.read(need)
   if not chunk:raise RuntimeError('Unexpected end of video: '+dec.stderr.read().decode())
   parts.append(chunk);need-=len(chunk)
  frame=Image.frombytes('RGB',(1080,1920),b''.join(parts));layer=graphics(n/60,source,words,cards);frame=Image.alpha_composite(frame.convert('RGBA'),layer).convert('RGB');enc.stdin.write(frame.tobytes())
  if n and n%360==0:print('source',source,'frames',n,'/',nframes,flush=True)
 enc.stdin.close();status=enc.wait();err=enc.stderr.read().decode();dec.stdout.close();dc=dec.wait()
 if status or dc:raise RuntimeError(err+dec.stderr.read().decode())
 print('source ready',source,out.stat().st_size,flush=True)
with ThreadPoolExecutor(max_workers=2) as p:list(p.map(render,[2,1]))
(R/'concat.txt').write_text(''.join(f"file '{(R/'public'/f'part-source-{i}.mp4').resolve()}'\n" for i in [2,1]))
