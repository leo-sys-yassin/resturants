from pathlib import Path
import subprocess,json,shutil,zipfile
R=Path(__file__).resolve().parent;D=R/'delivery';out=D/'Rexo_Velora_Motion_1080x1920.mp4'
subprocess.run(['ffmpeg','-y','-v','error','-i',str(D/'picture.mp4'),'-i',str(R/'voice.mp3'),'-i',str(D/'music.wav'),'-filter_complex','[1:a]aresample=48000,loudnorm=I=-16:TP=-1.5:LRA=11,apad=whole_dur=57.633333[a];[2:a]volume=1.0[m];[a][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89:level=false[out]','-map','0:v','-map','[out]','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(out)],check=True)
subprocess.run(['ffmpeg','-v','error','-i',str(out),'-f','null','-'],check=True)
data=json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_streams','-show_format','-of','json',str(out)]));(D/'technical-check.json').write_text(json.dumps(data,indent=2))
print('Verified',data['format']['duration'],data['format']['size'],flush=True)
