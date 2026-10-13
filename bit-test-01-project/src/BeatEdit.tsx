import {AbsoluteFill,staticFile,useVideoConfig} from 'remotion';
import {Video,Audio} from '@remotion/media';
export const BeatEdit = () => {
 const {fps}=useVideoConfig();
 return <AbsoluteFill style={{background:'#080909'}}>
  <Video name="Общий вид — speed ramp" src={staticFile('shot-1.mp4')} from={0} durationInFrames={2*fps} premountFor={fps} muted style={{width:'100%',height:'100%'}}/>
  <Video name="Передний бок — speed ramp" src={staticFile('shot-2.mp4')} from={2*fps} durationInFrames={2*fps} premountFor={fps} muted style={{width:'100%',height:'100%'}}/>
  <Video name="Двери — speed ramp" src={staticFile('shot-3.mp4')} from={4*fps} durationInFrames={2*fps} premountFor={fps} muted style={{width:'100%',height:'100%'}}/>
  <Video name="Задняя часть — speed ramp" src={staticFile('shot-4.mp4')} from={6*fps} durationInFrames={Math.round(119/60*fps)} premountFor={fps} muted style={{width:'100%',height:'100%'}}/>
  <Audio name="Funk — акценты и оригинальные свиши" src={staticFile('soundtrack.m4a')} premountFor={fps}/>
 </AbsoluteFill>;
};
