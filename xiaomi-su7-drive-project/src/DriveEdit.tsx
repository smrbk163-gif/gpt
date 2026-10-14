import {AbsoluteFill,staticFile,useVideoConfig} from "remotion";
import {Video,Audio} from "@remotion/media";
export const DriveEdit=()=>{const {fps}=useVideoConfig();return <AbsoluteFill style={{background:"#090B09"}}>
<Video name="ВСТРЕЧАЙ — XIAOMI SU7" src={staticFile("scene-1.mp4")} from={Math.round(0/60*fps)} durationInFrames={Math.round(137/60*fps)} premountFor={fps} muted style={{width:"100%",height:"100%"}}/>
<Video name="МОЩНОСТЬ — 299" src={staticFile("scene-2.mp4")} from={Math.round(137/60*fps)} durationInFrames={Math.round(136/60*fps)} premountFor={fps} muted style={{width:"100%",height:"100%"}}/>
<Video name="РАЗГОН — 5,28" src={staticFile("scene-3.mp4")} from={Math.round(273/60*fps)} durationInFrames={Math.round(137/60*fps)} premountFor={fps} muted style={{width:"100%",height:"100%"}}/>
<Video name="СИЛА НА ЗАДНИХ КОЛЁСАХ — RWD" src={staticFile("scene-4.mp4")} from={Math.round(410/60*fps)} durationInFrames={Math.round(136/60*fps)} premountFor={fps} muted style={{width:"100%",height:"100%"}}/>
<Video name="УДОБСТВО В ДЕТАЛЯХ — ЗЕРКАЛА" src={staticFile("scene-5.mp4")} from={Math.round(546/60*fps)} durationInFrames={Math.round(137/60*fps)} premountFor={fps} muted style={{width:"100%",height:"100%"}}/>
<Video name="СВЕТ — LED" src={staticFile("scene-6.mp4")} from={Math.round(683/60*fps)} durationInFrames={Math.round(136/60*fps)} premountFor={fps} muted style={{width:"100%",height:"100%"}}/>
<Video name="БАТАРЕЯ — 73,6" src={staticFile("scene-7.mp4")} from={Math.round(819/60*fps)} durationInFrames={Math.round(137/60*fps)} premountFor={fps} muted style={{width:"100%",height:"100%"}}/>
<Video name="ЗАПАС ХОДА — ДО 700" src={staticFile("scene-8.mp4")} from={Math.round(956/60*fps)} durationInFrames={Math.round(136/60*fps)} premountFor={fps} muted style={{width:"100%",height:"100%"}}/>
<Video name="БЫСТРАЯ ЗАРЯДКА — 15 МИН" src={staticFile("scene-9.mp4")} from={Math.round(1092/60*fps)} durationInFrames={Math.round(137/60*fps)} premountFor={fps} muted style={{width:"100%",height:"100%"}}/>
<Video name="МАКСИМАЛЬНАЯ СКОРОСТЬ — 210" src={staticFile("scene-10.mp4")} from={Math.round(1229/60*fps)} durationInFrames={Math.round(136/60*fps)} premountFor={fps} muted style={{width:"100%",height:"100%"}}/>
<Video name="ЭТОТ АВТОМОБИЛЬ — В САМАРЕ" src={staticFile("scene-11.mp4")} from={Math.round(1365/60*fps)} durationInFrames={Math.round(137/60*fps)} premountFor={fps} muted style={{width:"100%",height:"100%"}}/>
<Audio name="MAMA MA и оригинальные эффекты" src={staticFile("soundtrack.m4a")} premountFor={fps}/></AbsoluteFill>};
