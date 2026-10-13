from pathlib import Path
import json,subprocess
root=Path(__file__).resolve().parent.parent
fs=json.loads((root/'new-inputs.json').read_text())
for i,f in enumerate(fs):
 tr=root/'analysis'/f'stab-{i}.trf';out=root/'public'/f'stabilized-{i}.mp4'
 subprocess.run(['ffmpeg','-v','error','-y','-threads','2','-i',f,'-an','-vf',f'vidstabdetect=shakiness=5:accuracy=9:stepsize=12:mincontrast=0.2:result={tr}','-f','null','-'],check=True)
 subprocess.run(['ffmpeg','-v','error','-y','-threads','2','-i',f,'-an','-vf',f'vidstabtransform=input={tr}:smoothing=12:optalgo=gauss:maxshift=20:maxangle=0.012:zoom=4:optzoom=0:interpol=bicubic,crop=iw/1.015:ih/1.015,scale=1080:1920,setsar=1','-c:v','libx264','-threads','2','-crf','17','-preset','fast','-pix_fmt','yuv420p','-map_metadata','-1','-write_tmcd','0',str(out)],check=True)
 print('stabilized',i,flush=True)
