import React from 'react';
import {AbsoluteFill, Sequence, staticFile, useCurrentFrame, useVideoConfig, interpolate, spring, Easing} from 'remotion';
import {Video, Audio} from '@remotion/media';
import type {Caption} from '@remotion/captions';
import phrasesData from './phrases.json';
import {design, specifications} from './config';
import './style.css';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const ease = Easing.bezier(.16, 1, .3, 1);
const phrases: (Caption & {accent: string; strong?: boolean})[] = phrasesData;

export const ColorTreatment: React.FC<React.PropsWithChildren> = ({children}) => <AbsoluteFill style={{filter: `contrast(${design.color.contrast}) saturate(${design.color.saturation}) brightness(${design.color.brightness})`}}>{children}</AbsoluteFill>;
export const VideoBackground = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const time = frame/fps;
  // Reset on the original edits. Small scale changes preserve the face and car details.
  const zoom = time < 8.692 ? interpolate(time,[0,4,8.692],[1,1+design.cameraZoom*.7,1],{...clamp,easing:Easing.inOut(Easing.cubic)})
    : time < 13.797 ? interpolate(time,[8.692,11,13.797],[1,1+design.cameraZoom*.55,1],{...clamp,easing:Easing.inOut(Easing.cubic)})
      : interpolate(time,[13.797,16.5,19.7],[1,1+design.cameraZoom,1.002],{...clamp,easing:Easing.inOut(Easing.cubic)});
  return <ColorTreatment><AbsoluteFill style={{scale:zoom,transformOrigin:'60% 48%'}}><Video name="Исходный видеоряд — плавная камера" src={staticFile('footage.mp4')} muted premountFor={fps} objectFit="contain" style={{width:'100%',height:'100%'}}/></AbsoluteFill></ColorTreatment>;
};
export const AudioLayer = () => {
  const {fps} = useVideoConfig();
  return <>
    <Audio name="Оригинальная речь" src={staticFile('voice.m4a')} premountFor={fps}/>
    <Sequence name="Мощность — whoosh и низкий удар" from={13.8*fps} durationInFrames={fps} premountFor={fps}><Audio src={staticFile('sfx-power.wav')} volume={design.soundVolume} premountFor={fps}/></Sequence>
    <Sequence name="Три мотора — три электрических щелчка" from={16.08*fps} durationInFrames={fps} premountFor={fps}><Audio src={staticFile('sfx-motors.wav')} volume={design.soundVolume} premountFor={fps}/></Sequence>
    <Sequence name="Разгон — нарастающий свип" from={18.5*fps} durationInFrames={fps} premountFor={fps}><Audio src={staticFile('sfx-acceleration.wav')} volume={design.soundVolume} premountFor={fps}/></Sequence>
  </>;
};

export const AnimatedShade = ({local, remaining, top, height}:{local:number;remaining:number;top:number;height:number}) => <div style={{
  position:'absolute',left:0,top,width:1080,height,pointerEvents:'none',
  background:`radial-gradient(ellipse at center, rgba(0,0,0,${design.shadeOpacity}) 0%, rgba(0,0,0,.58) 36%, rgba(0,0,0,.18) 62%, transparent 78%)`,
  opacity:Math.min(interpolate(local,[0,10],[0,1],clamp),interpolate(remaining,[0,5],[0,1],clamp)),
  translate:`0 ${interpolate(local,[0,15],[30,0],{...clamp,easing:ease})}px`,
}}/>;

// This stagger is the entrance of a whole phrase, not measured speech word timing.
export const KineticTypography = ({caption}:{caption:(typeof phrases)[number]}) => {
  const frame=useCurrentFrame();const {fps}=useVideoConfig();
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
  const frame=useCurrentFrame();const {fps}=useVideoConfig();
  const active=phrases.find(c=>frame/fps*1000>=c.startMs&&frame/fps*1000<c.endMs);
  if(!active)return null;
  return <>
    <AnimatedShade local={frame-active.startMs/1000*fps} remaining={active.endMs/1000*fps-frame} top={1920-design.subtitleBottom-205} height={350}/>
    <div style={{position:'absolute',bottom:design.subtitleBottom,left:90,width:design.subtitleWidth}}><KineticTypography caption={active}/></div>
  </>;
};

export const AnimatedCounter = ({value,digits,local}:{value:number;digits:number;local:number}) => {
  const {fps}=useVideoConfig();
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

export const TechnicalAnimation = ({kind,local}:{kind:number;local:number}) => {
  const {fps}=useVideoConfig();
  const progress=interpolate(local,[5,23],[0,1],{...clamp,easing:ease});
  const exitFlash=interpolate(local,[8,14,23],[0,.35,0],clamp);
  return <svg width="900" height="90" viewBox="0 0 900 90" style={{display:'block',overflow:'visible'}}>
    {kind===1401&&<>
      <path d="M260 47 H300 L317 28 L334 63 L356 18 L378 72 L400 36 L420 47 H640" fill="none" stroke={design.accent} strokeWidth="4" strokeDasharray="620" strokeDashoffset={(1-progress)*620}/>
      <path d="M260 47 H640" stroke={design.white} strokeOpacity=".2"/>
      <circle cx={260+380*progress} cy="47" r="5" fill={design.accent}/>
      <path d="M230 30 V64 H251 M670 30 V64 H649" stroke={design.accent} strokeWidth="2" fill="none" opacity={progress}/>
    </>}
    {kind===3&&<>
      <path d="M330 45 H570" stroke={design.accent} strokeOpacity=".35" strokeDasharray="240" strokeDashoffset={(1-progress)*240}/>
      {[330,450,570].map((x,i)=>{
        const p=spring({frame:local-5-i*3,fps,durationInFrames:17,config:{damping:18}});
        return <g key={i} opacity={Math.min(1,p)} style={{translate:`${x}px 45px`,scale:p,rotate:`${(1-p)*100}deg`}}>
          <circle r="29" stroke={design.accent} strokeWidth="3" fill="rgba(0,0,0,.15)"/>
          <path d="M-17 -9 H17 V9 H-17 Z M-23 -5 H-17 M17 -5 H23 M-23 5 H-17 M17 5 H23 M-8 -15 V-9 M8 -15 V-9" fill="none" stroke={design.white} strokeWidth="2"/>
          <path d="M2 -7 L-5 2 H2 L-2 9 L7 -2 H1 Z" fill={design.accent}/>
        </g>;
      })}
    </>}
    {kind===3.1&&<>
      <path d="M200 64 H700 M220 20 V64" stroke={design.white} strokeOpacity=".24"/>
      <path d="M220 59 C380 59 430 52 485 39 S600 12 680 12" fill="none" stroke={design.accent} strokeWidth="4" strokeDasharray="490" strokeDashoffset={(1-progress)*490}/>
      {[0,1,2,3,4,5].map(i=><path key={i} d={`M${250+i*80} 61 V68`} stroke={design.white} strokeOpacity=".35"/>)}
      <path d="M668 3 L681 12 L668 21" fill="none" stroke={design.accent} strokeWidth="3" opacity={progress}/>
      <path d="M220 60 H680" stroke={design.accent} strokeWidth="7" opacity={exitFlash}/>
    </>}
  </svg>;
};

export const SpecificationOverlay = ({spec}:{spec:(typeof specifications)[number]}) => {
  const frame=useCurrentFrame();const {fps}=useVideoConfig();
  const local=frame-spec.start*fps;const remaining=spec.end*fps-frame;
  return <>
    <AnimatedShade local={local} remaining={remaining} top={-30} height={680}/>
    <div style={{position:'absolute',left:90,top:118,width:900,textAlign:'center',
      opacity:interpolate(remaining,[0,5],[0,1],clamp),translate:`0 ${interpolate(remaining,[0,6],[-35,0],clamp)}px`,
    }}>
      <div style={{height:42,overflow:'hidden'}}><div style={{fontSize:25,letterSpacing:5,
        translate:`0 ${interpolate(local,[2,15],[55,0],{...clamp,easing:ease})}px`,
      }}>{spec.title}</div></div>
      <div style={{scale:interpolate(local,[3,20],[1.15,1],{...clamp,easing:ease}),
        clipPath:`inset(0 ${interpolate(local,[2,13],[48,0],{...clamp,easing:ease})}% 0 ${interpolate(local,[2,13],[48,0],{...clamp,easing:ease})}%)`,
      }}><AnimatedCounter value={spec.value} digits={spec.digits} local={local}/></div>
      <div style={{height:44,overflow:'hidden'}}><div style={{fontSize:30,letterSpacing:2,
        translate:`0 ${interpolate(local,[8,21],[60,0],{...clamp,easing:ease})}px`,
      }}>{spec.unit}</div></div>
      <TechnicalAnimation kind={spec.value} local={local}/>
      <svg width="900" height="1" style={{position:'absolute',top:155,left:0,overflow:'visible',pointerEvents:'none'}}>
        <path d="M120 -65 L60 65 M780 -65 L840 65" stroke={design.accent} strokeWidth="3" opacity={interpolate(local,[2,8,18],[0,.7,0],clamp)}/>
      </svg>
    </div>
  </>;
};
export const MotionGraphics = () => {
  const frame=useCurrentFrame();const {fps}=useVideoConfig();const time=frame/fps;
  const spec=specifications.find(s=>time>=s.start&&time<s.end);const modelFrame=frame-2.8*fps;
  return <>
    {time>=2.8&&time<4.65&&<>
      <AnimatedShade local={modelFrame} remaining={4.65*fps-frame} top={20} height={540}/>
      <div style={{position:'absolute',left:90,top:170,width:900,textAlign:'center',overflow:'hidden',fontStyle:'italic',opacity:interpolate(time,[4.4,4.65],[1,0],clamp)}}>
        <div style={{fontSize:100,letterSpacing:'-4px',translate:`0 ${interpolate(modelFrame,[3,18],[140,0],{...clamp,easing:ease})}px`}}>ZEEKR 9X</div>
        <div style={{fontSize:54,color:design.accent,letterSpacing:12,translate:`0 ${interpolate(modelFrame,[8,23],[85,0],{...clamp,easing:ease})}px`}}>HYPER</div>
      </div>
    </>}
    {spec&&<SpecificationOverlay spec={spec}/>}
  </>;
};
export const MainComposition = () => <AbsoluteFill style={{background:'#080B0A',color:design.white,fontFamily:design.fontFamily,fontWeight:900}}>
  <VideoBackground/><MotionGraphics/><AnimatedSubtitles/><AudioLayer/>
</AbsoluteFill>;
export const StyleTest = () => {
  const {fps}=useVideoConfig();
  return <Sequence name="Тест: мощность, моторы, разгон" trimBefore={13.8*fps} durationInFrames={5.9*fps} premountFor={fps}><MainComposition/></Sequence>;
};
