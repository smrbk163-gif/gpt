import React from 'react';
import {AbsoluteFill, Sequence, staticFile, useCurrentFrame, useVideoConfig, interpolate, spring, Easing} from 'remotion';
import {Video, Audio} from '@remotion/media';
import type {Caption} from '@remotion/captions';
import phrasesData from './phrases.json';
import {design} from './config';
import './style.css';

// Preserve approved timings while evaluating motion at 60fps.
const useAnimationFrame = () => useCurrentFrame()*30/useVideoConfig().fps;
const useAnimationConfig = () => ({fps:30});

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const ease = Easing.bezier(.16, 1, .3, 1);
const phrases: (Caption & {accent: string; strong?: boolean})[] = phrasesData;

export const ColorTreatment: React.FC<React.PropsWithChildren> = ({children}) => <AbsoluteFill style={{filter: `contrast(${design.color.contrast}) saturate(${design.color.saturation}) brightness(${design.color.brightness})`}}>{children}</AbsoluteFill>;
export const VideoBackground = () => {
  const frame = useAnimationFrame();
  const {fps} = useAnimationConfig();
  const time = frame/fps;
  // Reset on the original edits. Small scale changes preserve the face and car details.
  const zoom = time < 5.338667 ? interpolate(time,[0,2.7,5.338667],[1,1.025,1],{...clamp,easing:Easing.inOut(Easing.cubic)})
    : time < 13.86385 ? interpolate(time,[5.338667,9.7,13.86385],[1,1.022,1],{...clamp,easing:Easing.inOut(Easing.cubic)})
      : interpolate(time,[13.86385,17,19.37],[1,1.038,1.005],{...clamp,easing:Easing.inOut(Easing.cubic)});
  return <ColorTreatment><AbsoluteFill style={{scale:zoom,transformOrigin:time<13.86385?'50% 45%':'40% 44%'}}><Video name="Исходный видеоряд — плавная камера" src={staticFile('footage.mp4')} muted premountFor={fps} objectFit="contain" style={{width:'100%',height:'100%'}}/></AbsoluteFill></ColorTreatment>;
};
export const AudioLayer = () => {
 const {fps}=useVideoConfig();
 return <><Audio name="Оригинальная речь" src={staticFile('voice.m4a')} premountFor={fps}/>
 {([{kind:'mass',start:2.99},{kind:'emotion',start:8.87},{kind:'telegram',start:16.95}]).map(s=><Sequence key={s.kind} name={s.kind+' — звуковой акцент'} from={Math.round(s.start*fps)} durationInFrames={fps} premountFor={fps}><Audio src={staticFile('sfx-'+s.kind+'.wav')} volume={design.soundVolume} premountFor={fps}/></Sequence>)}</>;
};

export const AnimatedShade = ({local, remaining, top, height}:{local:number;remaining:number;top:number;height:number}) => <div style={{
  position:'absolute',left:0,top,width:1080,height,pointerEvents:'none',
  background:`radial-gradient(ellipse at center, rgba(0,0,0,${design.shadeOpacity}) 0%, rgba(0,0,0,.58) 36%, rgba(0,0,0,.18) 62%, transparent 78%)`,
  opacity:Math.min(interpolate(local,[0,10],[0,1],clamp),interpolate(remaining,[0,5],[0,1],clamp)),
  translate:`0 ${interpolate(local,[0,15],[30,0],{...clamp,easing:ease})}px`,
}}/>;

// This stagger is the entrance of a whole phrase, not measured speech word timing.
export const KineticTypography = ({caption}:{caption:(typeof phrases)[number]}) => {
  const frame=useAnimationFrame();const {fps}=useAnimationConfig();
  const local=frame-caption.startMs/1000*fps;const end=caption.endMs/1000*fps;
  const words=caption.text.replace(/[,.]$/,'').split(' ');
  return <div style={{fontSize:caption.strong?58:design.subtitleSize,fontWeight:900,fontStyle:'italic',lineHeight:1.18,letterSpacing:'-1.4px',textTransform:'uppercase',textAlign:'center',
    opacity:interpolate(frame,[end-4,end],[1,0],clamp),translate:`0 ${interpolate(frame,[end-5,end],[0,-22],clamp)}px`,
  }}>
    {words.map((word,i)=>{
      const emphasized=Boolean(caption.accent)&&caption.accent.toUpperCase().includes(word.toUpperCase());
      const offset=3+Math.min(i*1.5,6);
      return <span key={i} style={{display:'inline-block',overflow:'hidden',verticalAlign:'bottom',padding:'7px 10px'}}>
        <span style={{display:'inline-block',color:emphasized?design.accent:design.white,
          translate:`0 ${interpolate(local,[offset,offset+12],[90,0],{...clamp,easing:ease})}px`,
          scale:interpolate(local,[offset,offset+12],[1.12,1],{...clamp,easing:ease}),
          opacity:interpolate(local,[offset,offset+4],[0,1],clamp),
        }}>{word}</span>
      </span>;
    })}
  </div>;
};
export const AnimatedSubtitles = () => {
  const frame=useAnimationFrame();const {fps}=useAnimationConfig();
  const active=phrases.find(c=>frame/fps*1000>=c.startMs&&frame/fps*1000<c.endMs);
  if(!active)return null;
  return <>
    <AnimatedShade local={frame-active.startMs/1000*fps} remaining={active.endMs/1000*fps-frame} top={1920-design.subtitleBottom-205} height={350}/>
    <div style={{position:'absolute',bottom:design.subtitleBottom,left:90,width:design.subtitleWidth}}><KineticTypography caption={active}/></div>
  </>;
};

export const AnimatedCounter = ({value,digits,local}:{value:number;digits:number;local:number}) => {
  const {fps}=useAnimationConfig();
  const chars=value.toLocaleString('ru-RU',{minimumFractionDigits:digits,maximumFractionDigits:digits}).split('');
  return <div style={{display:'flex',justifyContent:'center',alignItems:'center',height:224,overflow:'hidden',fontSize:202,lineHeight:'224px',fontStyle:'italic',fontVariantNumeric:'tabular-nums',letterSpacing:'-9px'}}>
    {chars.map((char,i)=>{
      if(!/\d/.test(char))return <span key={i} style={{width:char===','?48:32,flexShrink:0}}>{char}</span>;
      const target=Number(char);
      const progress=spring({frame:local-3-i*1.2,fps,durationInFrames:19,config:{damping:18,stiffness:150,mass:.8}});
      return <div key={i} style={{height:224,width:142,overflow:'hidden',flexShrink:0}}>
        <div style={{translate:`0 ${-progress*672}px`}}>{[3,2,1,0].map(n=><div key={n} style={{height:224,background:'linear-gradient(180deg,#D9FF00 12%,#BFFF00 55%,#79D700 100%)',backgroundClip:'text',WebkitBackgroundClip:'text',color:'transparent'}}>{(target+n)%10}</div>)}</div>
      </div>;
    })}
  </div>;
};

const Reveal = ({local,delay=3,children,style={}}:{local:number;delay?:number;children:React.ReactNode;style?:React.CSSProperties}) => <div style={{overflow:'hidden',...style}}><div style={{translate:`0 ${interpolate(local,[delay,delay+15],[130,0],{...clamp,easing:ease})}px`,opacity:interpolate(local,[delay,delay+5],[0,1],clamp)}}>{children}</div></div>;
export const MotionGraphics = () => {
 const frame=useAnimationFrame();const {fps}=useAnimationConfig();const time=frame/fps;
 const kind=time>=2.99&&time<5.33?'mass':time>=8.87&&time<11.3?'emotion':time>=16.95&&time<19.27?'telegram':null;
 if(!kind)return null;
 const start=kind==='mass'?2.99:kind==='emotion'?8.87:16.95;
 const end=kind==='mass'?5.33:kind==='emotion'?11.3:19.27;
 const local=frame-start*fps,remaining=end*fps-frame;
 const draw=interpolate(local,[7,26],[0,1],{...clamp,easing:ease});
 const plane=spring({frame:local-3,fps,durationInFrames:22,config:{damping:19,stiffness:130}});
 return <><AnimatedShade local={local} remaining={remaining} top={-65} height={660}/>
 <div style={{position:'absolute',top:120,left:90,width:900,textAlign:'center',opacity:interpolate(remaining,[0,5],[0,1],clamp),translate:`0 ${interpolate(remaining,[0,6],[-30,0],clamp)}px`}}>
 {kind==='mass'&&<>
 <Reveal local={local} style={{fontSize:30,letterSpacing:6}}>МАССА — БОЛЕЕ</Reveal>
 <div style={{clipPath:`inset(0 ${(1-draw)*45}% 0 ${(1-draw)*45}%)`}}><AnimatedCounter value={3.5} digits={1} local={local}/></div>
 <Reveal local={local} delay={8} style={{fontSize:38,letterSpacing:7}}>ТОНН</Reveal>
 <svg width="900" height="95" viewBox="0 0 900 95"><path d="M300 67 H600 M320 62 L339 27 H561 L580 62 Z" stroke={design.accent} strokeWidth="4" fill="none" strokeDasharray="660" strokeDashoffset={(1-draw)*660}/><path d="M375 27 L396 12 H504 L525 27 M350 76 L358 82 L366 76 L374 82 L382 76 M518 76 L526 82 L534 76 L542 82 L550 76" stroke="white" strokeWidth="3" fill="none" opacity={draw}/></svg>
 </>}
 {kind==='emotion'&&<>
 <Reveal local={local} style={{fontSize:76,fontStyle:'italic',letterSpacing:-2}}>СЧАСТЬЕ</Reveal>
 <Reveal local={local} delay={7} style={{fontSize:91,fontStyle:'italic',color:design.accent,letterSpacing:-3}}>В ЭМОЦИЯХ</Reveal>
 <svg width="900" height="100" viewBox="0 0 900 100"><path d="M100 12 V62 H125 M800 12 V62 H775 M160 51 C310 75 610 5 740 29" fill="none" stroke={design.accent} strokeWidth="4" strokeDasharray="780" strokeDashoffset={(1-draw)*780}/>{[0,1,2].map(i=><circle key={i} cx={345+i*105} cy={60+i%2*12} r={4} fill="white" opacity={interpolate(local,[12+i*3,18+i*3],[0,1],clamp)}/>)}</svg>
 </>}
 {kind==='telegram'&&<>
 <svg width="900" height="95" viewBox="0 0 900 95" style={{overflow:'visible'}}><path d="M130 70 C240 20 310 85 405 45" fill="none" stroke={design.accent} strokeWidth="3" strokeDasharray="350" strokeDashoffset={(1-draw)*350} opacity={interpolate(local,[5,18,30],[0,.75,0],clamp)}/><g transform={`translate(${450-(1-plane)*330} ${44+(1-plane)*55}) rotate(${(1-plane)*-25}) scale(${.7+.3*plane})`} opacity={Math.min(1,plane)}><path d="M-43 0 L43 -28 L18 37 L-3 12 L-43 0 Z M-3 12 L43 -28 M-3 12 L-6 29 L5 21" stroke={design.accent} strokeWidth="4" fill="rgba(0,0,0,.15)" strokeLinejoin="round"/></g></svg>
 <Reveal local={local} delay={6} style={{fontSize:35,letterSpacing:4}}>ПОДРОБНЕЕ В</Reveal>
 <Reveal local={local} delay={10} style={{fontSize:92,fontStyle:'italic',color:design.accent,letterSpacing:-3}}>TELEGRAM</Reveal>
 {time>=17.95&&<Reveal local={frame-17.95*fps} delay={0} style={{fontSize:29,letterSpacing:1,marginTop:20}}>В ОПИСАНИИ ПРОФИЛЯ</Reveal>}
 </>}
 </div></>;
};
export const MainComposition = () => <AbsoluteFill style={{background:'#080B0A',color:design.white,fontFamily:design.fontFamily,fontWeight:900}}><VideoBackground/><MotionGraphics/><AnimatedSubtitles/><AudioLayer/></AbsoluteFill>;
