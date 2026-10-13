import {AbsoluteFill,staticFile,useVideoConfig} from "remotion";
import {Video,Audio} from "@remotion/media";
export const BeatEdit = () => { const {fps}=useVideoConfig(); return <AbsoluteFill style={{background:"#080909"}}>
<Video name="Общий вид" src={staticFile("shot-1.mp4")} from={0*fps} durationInFrames={2*fps} premountFor={fps} muted style={{width:"100%",height:"100%"}}/>
<Video name="Передний бок — быстрая перебивка" src={staticFile("shot-2.mp4")} from={2*fps} durationInFrames={fps} premountFor={fps} muted style={{width:"100%",height:"100%"}}/>
<Video name="Передний ракурс — стабилизация" src={staticFile("shot-3.mp4")} from={3*fps} durationInFrames={2*fps} premountFor={fps} muted style={{width:"100%",height:"100%"}}/>
<Video name="Двери — быстрая перебивка" src={staticFile("shot-4.mp4")} from={5*fps} durationInFrames={fps} premountFor={fps} muted style={{width:"100%",height:"100%"}}/>
<Video name="Заднее колесо" src={staticFile("shot-5.mp4")} from={6*fps} durationInFrames={2*fps} premountFor={fps} muted style={{width:"100%",height:"100%"}}/>
<Video name="Задний ракурс — стабилизация" src={staticFile("shot-6.mp4")} from={8*fps} durationInFrames={4*fps} premountFor={fps} muted style={{width:"100%",height:"100%"}}/>
<Video name="Финал у выезда — стабилизация" src={staticFile("shot-7.mp4")} from={12*fps} durationInFrames={Math.round(239/60*fps)} premountFor={fps} muted style={{width:"100%",height:"100%"}}/>
<Audio name="Funk и шесть оригинальных свишей" src={staticFile("soundtrack.m4a")} premountFor={fps}/></AbsoluteFill>; };
