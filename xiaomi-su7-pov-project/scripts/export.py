from pathlib import Path
import subprocess,json
R=Path(__file__).resolve().parent.parent
out=R/'SU7-First-Person-V2-1080x1920-60fps.mp4'
subprocess.run(['ffmpeg','-v','warning','-y','-f','concat','-safe','0','-i',str(R/'concat.txt'),'-i',str(R/'public/soundtrack.m4a'),'-map','0:v:0','-map','1:a:0','-c','copy','-bsf:v','h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=6:video_full_range_flag=0','-map_metadata','-1','-movflags','+faststart',str(out)],check=True)
assert out.stat().st_size<104857600, 'Drive upload limit exceeded'
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(out)]));v=next(s for s in probe['streams'] if s['codec_type']=='video');assert (v['width'],v['height'],v['avg_frame_rate'],v['nb_frames'])==(1080,1920,'60/1','3444')
subprocess.run(['ffmpeg','-v','error','-threads','2','-i',str(out),'-f','null','-'],check=True)
(R/'analysis/qa.json').write_text(json.dumps(probe,indent=2));print(out,out.stat().st_size,flush=True)
