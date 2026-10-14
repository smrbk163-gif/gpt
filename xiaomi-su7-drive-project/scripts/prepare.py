from pathlib import Path
import subprocess,json,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
r=Path(__file__).resolve().parent.parent;inputs={i['name']:i for i in json.loads((r/'inputs.json').read_text())};scenes=json.loads((r/'scenes.json').read_text());lime='#BFFF00'
def font(n,italic=False):return ImageFont.truetype(str(r/'fonts'/('Montserrat-900-italic.ttf' if italic else 'Montserrat-900-normal.ttf')),n)
def save_text(text,y,size,path,color='white',italic=False):
 im=Image.new('RGBA',(1080,1920));d=ImageDraw.Draw(im);f=font(size,italic)
 while d.textbbox((0,0),text,font=f)[2]>880:size-=2;f=font(size,italic)
 d.text((540,y),text,font=f,fill=color,anchor='mt');im.save(path)
for i,s in enumerate(scenes):
 base=r/'analysis'/f'g{i}';base.mkdir(exist_ok=True);bottom=s['kind']=='mirror';y=1220 if bottom else 135
 save_text(s['label'],y,29,base/'label.png')
 size=166 if len(s['value'])<=6 else 102
 save_text(s['value'],y+55,size,base/'value.png',lime,True)
 save_text(s['unit'],y+(245 if len(s['value'])<=6 else 190),31,base/'unit.png')
 # Local shading is separate from type; no text shadows.
 yy,xx=np.mgrid[0:1920,0:1080];cy=y+165;alpha=np.clip(1-(((xx-540)/660)**2+((yy-cy)/390)**2),0,1)**1.8*.78
 a=np.zeros((1920,1080,4),dtype=np.uint8);a[:,:,3]=(alpha*255).astype(np.uint8);Image.fromarray(a).save(base/'shade.png')
 im=Image.new('RGBA',(1080,1920));d=ImageDraw.Draw(im);iy=y+330;kind=s['kind']
 if kind=='power':d.line([(260,iy+35),(340,iy+35),(370,iy+5),(400,iy+60),(440,iy-5),(480,iy+65),(520,iy+20),(560,iy+35),(820,iy+35)],fill=lime,width=5)
 elif kind in ['accel','speed']:
  d.line([(270,iy+65),(810,iy+65)],fill='#FFFFFF66',width=2);d.line([(290,iy+55),(390,iy+53),(485,iy+40),(570,iy+16),(660,iy),(800,iy-4)],fill=lime,width=5);d.line([(780,iy-20),(800,iy-4),(780,iy+12)],fill=lime,width=5)
 elif kind=='drive':
  for x in [365,650]:d.rounded_rectangle((x,iy-5,x+65,iy+80),radius=15,outline=lime,width=4)
  d.line([(430,iy+38),(650,iy+38)],fill='white',width=4);d.ellipse((510,iy+12,570,iy+70),outline=lime,width=4)
 elif kind=='mirror':
  d.rounded_rectangle((395,iy-5,590,iy+75),radius=24,outline=lime,width=4);d.line([(590,iy+35),(650,iy+60),(665,iy+60)],fill='white',width=5);d.arc((345,iy-40,690,iy+130),190,300,fill=lime,width=4);d.polygon([(655,iy-18),(675,iy-9),(657,iy+6)],fill=lime)
 elif kind=='light':
  d.rounded_rectangle((360,iy-10,530,iy+72),radius=25,outline='white',width=4)
  for j in range(3):d.line([(570,iy+j*25),(735+j*20,iy+j*25)],fill=lime,width=5)
 elif kind in ['battery','charge']:
  d.rounded_rectangle((350,iy-8,730,iy+70),radius=13,outline='white',width=4);d.rectangle((731,iy+12,750,iy+48),fill='white')
  for j in range(4):d.rounded_rectangle((365+j*87,iy+5,435+j*87,iy+56),radius=4,fill=lime)
  if kind=='charge':d.polygon([(545,iy-16),(520,iy+27),(544,iy+27),(529,iy+80),(568,iy+19),(544,iy+19)],fill='#141A10')
 elif kind=='range':
  pts=[(270,iy+50),(350,iy+50),(395,iy+10),(650,iy+10),(710,iy+50),(810,iy+50)];d.line(pts,fill=lime,width=4)
  for x,dy in [(270,50),(810,50)]:d.ellipse((x-10,iy+dy-10,x+10,iy+dy+10),fill='white')
 elif kind=='end':
  d.ellipse((516,iy-10,564,iy+38),outline=lime,width=4);d.line([(520,iy+31),(540,iy+68),(560,iy+31)],fill=lime,width=4)
 else:d.line([(300,iy+18),(780,iy+18)],fill=lime,width=5)
 im.save(base/'icon.png')
 dur=s['frames']/60;src=inputs[s['source']];total=float(src['meta']['format']['duration']);start=.06;end=total-.12;span=end-start;k=.45
 pts=f'{dur}*((T-{start})/{span}-{k}*sin(2*PI*(T-{start})/{span})/(2*PI))/TB'
 zoom=f'1.012+.01*sin(PI*on/{s["frames"]-1})+.055*exp(-on/2.5)+.075*exp(-({s["frames"]-1}-on)/2.5)'
 vf=f"trim=start={start}:end={end},setpts='{pts}',scale=1080:1920,framerate=fps=60:interp_start=15:interp_end=240:scene=100,tpad=stop_mode=clone:stop_duration=0.1,trim=end_frame={s['frames']},zoompan=z='{zoom}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=1080x1920:fps=60,eq=contrast=1.025:saturation=.98,setsar=1"
 vid=r/'public'/f'video-{i+1}.mp4';out=r/'public'/f'scene-{i+1}.mp4'
 subprocess.run(['ffmpeg','-v','error','-y','-threads','2','-i',src['path'],'-map','0:v:0','-an','-vf',vf,'-c:v','libx264','-threads','2','-preset','fast','-crf','20','-pix_fmt','yuv420p','-map_metadata','-1','-write_tmcd','0',str(vid)],check=True)
 args=['ffmpeg','-v','error','-y','-threads','2','-i',str(vid)];layers=['shade','label','value','unit','icon']
 for name in layers:args+=['-loop','1','-framerate','60','-i',str(base/(name+'.png'))]
 filters=[];last='0:v'
 for j,name in enumerate(layers):
  delay=[0,.055,.105,.19,.3][j];outtag=f'v{j}';filters.append(f'[{j+1}:v]format=rgba,fade=t=in:st={delay}:d=0.17:alpha=1,fade=t=out:st={dur-.15}:d=0.15:alpha=1[l{j}]')
  yy='0' if j==0 else f'if(lt(t,{delay+.35}),65*pow(1-min(1,max(0,(t-{delay})/.35)),3),0)'
  filters.append(f'[{last}][l{j}]overlay=x=0:y=\'{yy}\':shortest=1[{outtag}]');last=outtag
 args+=['-filter_complex_threads','2','-filter_complex',';'.join(filters),'-map',f'[{last}]','-an','-frames:v',str(s['frames']),'-c:v','libx264','-threads','2','-preset','fast','-b:v','3400k','-maxrate','4600k','-bufsize','6800k','-pix_fmt','yuv420p','-map_metadata','-1','-write_tmcd','0',str(out)]
 subprocess.run(args,check=True);print('prepared scene',i+1,s['kind'],flush=True)
(r/'concat.txt').write_text(''.join(f"file '{(r/'public'/f'scene-{i+1}.mp4').resolve()}'\n" for i in range(len(scenes))))
