import {AbsoluteFill,staticFile} from 'remotion';
import {Video,Audio} from '@remotion/media';
export const DriveEdit=()=> <AbsoluteFill style={{background:'#090F0F'}}>
<Video name="Обход автомобиля · речь · HUD" src={staticFile('part-source-2.mp4')} from={0} durationInFrames={1717} premountFor={60} muted style={{width:'100%',height:'100%'}}/>
<Video name="Салон и задняя часть · речь · HUD" src={staticFile('part-source-1.mp4')} from={1717} durationInFrames={1727} premountFor={60} muted style={{width:'100%',height:'100%'}}/>
<Audio name="Оригинальный голос · звуки интерфейса" src={staticFile('soundtrack.m4a')}/>
</AbsoluteFill>;
