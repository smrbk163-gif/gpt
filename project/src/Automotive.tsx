import React from 'react';
import {AbsoluteFill, Sequence, staticFile, useCurrentFrame, useVideoConfig, interpolate, spring, Easing} from 'remotion';
import {Video, Audio} from '@remotion/media';
import type {Caption} from '@remotion/captions';
import phrasesData from './phrases.json';
import {design, specifications} from './config';
import './style.css';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const ease = Easing.bezier(0.16, 1, 0.3, 1);
const phrases: (Caption & {accent: string; strong?: boolean})[] = phrasesData;

export const ColorTreatment: React.FC<React.PropsWithChildren> = ({children}) => <AbsoluteFill style={{filter: `contrast(${design.color.contrast}) saturate(${design.color.saturation}) brightness(${design.color.brightness})`}}>{children}</AbsoluteFill>;
export const VideoBackground = () => {
  const {fps} = useVideoConfig();
  return <ColorTreatment><Video name="Исходный видеоряд" src={staticFile('footage.mp4')} muted premountFor={fps} objectFit="contain" style={{width: '100%', height: '100%'}}/></ColorTreatment>;
};
export const AudioLayer = () => {
  const {fps} = useVideoConfig();
  return <>
    <Audio name="Оригинальная речь" src={staticFile('voice.m4a')} premountFor={fps}/>
    <Audio name="Авторские мягкие акценты" src={staticFile('accents.wav')} volume={design.soundVolume} premountFor={fps}/>
  </>;
};

// Stagger is an entrance animation, not invented word-level speech alignment.
export const KineticTypography = ({caption}: {caption: (typeof phrases)[number]}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const local = frame - caption.startMs / 1000 * fps;
  const end = caption.endMs / 1000 * fps;
  const words = caption.text.replace(/[,.]$/, '').split(' ');
  return <div style={{
    fontSize: caption.strong ? 61 : design.subtitleSize, fontWeight: 900,
    lineHeight: 1.16, letterSpacing: '-2px', textTransform: 'uppercase',
    textAlign: 'center', textShadow: '0 4px 18px rgba(0,0,0,.9), 0 2px 4px #000',
    opacity: interpolate(frame, [end-4, end], [1, 0], clamp),
    translate: `0 ${interpolate(frame, [end-5, end], [0, -16], clamp)}px`,
  }}>
    {words.map((word, i) => {
      const emphasized = Boolean(caption.accent) && caption.accent.toUpperCase().includes(word.toUpperCase());
      const offset = Math.min(i * 1.5, 6);
      return <span key={i} style={{display: 'inline-block', overflow: 'hidden', verticalAlign: 'bottom', padding: '5px 7px'}}>
        <span style={{display: 'inline-block', color: emphasized ? design.accent : design.white,
          translate: `0 ${interpolate(local, [offset, offset+12], [85, 0], {...clamp, easing: ease})}px`,
          scale: interpolate(local, [offset, offset+12], [1.09, 1], {...clamp, easing: ease}),
          opacity: interpolate(local, [offset, offset+4], [0, 1], clamp),
        }}>{word}</span>
      </span>;
    })}
  </div>;
};
export const AnimatedSubtitles = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const active = phrases.find(c => frame/fps*1000 >= c.startMs && frame/fps*1000 < c.endMs);
  return active ? <div style={{position: 'absolute', bottom: design.subtitleBottom, left: 90, width: design.subtitleWidth}}><KineticTypography caption={active}/></div> : null;
};

// Each numeral rolls through a deterministic short strip and settles at the stated value.
export const AnimatedCounter = ({value, digits, local}: {value: number; digits: number; local: number}) => {
  const {fps} = useVideoConfig();
  const chars = value.toLocaleString('ru-RU', {minimumFractionDigits: digits, maximumFractionDigits: digits}).split('');
  return <div style={{display: 'flex', alignItems: 'center', height: 202, overflow: 'hidden', fontSize: 184, lineHeight: '202px', fontVariantNumeric: 'tabular-nums', letterSpacing: '-8px'}}>
    {chars.map((char, i) => {
      if (!/\d/.test(char)) return <span key={i} style={{width: char === ',' ? 45 : 30, flexShrink: 0}}>{char}</span>;
      const target = Number(char);
      const progress = spring({frame: local-i*1.2, fps, durationInFrames: 18, config: {damping: 17, stiffness: 145, mass: .8}});
      return <div key={i} style={{height: 202, width: 126, overflow: 'hidden', flexShrink: 0}}>
        <div style={{translate: `0 ${-progress*606}px`}}>
          {[3,2,1,0].map((n) => <div key={n} style={{height: 202}}>{(target+n)%10}</div>)}
        </div>
      </div>;
    })}
  </div>;
};

export const SpecificationOverlay = ({spec}: {spec: (typeof specifications)[number]}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const local = frame-spec.start*fps;
  const end = spec.end*fps;
  return <div style={{position: 'absolute', left: 90, top: 175, width: 730,
    opacity: interpolate(frame, [end-5, end], [1, 0], clamp),
    translate: `${interpolate(frame, [end-5, end], [0, 35], clamp)}px 0`,
    textShadow: '0 4px 20px rgba(0,0,0,.72)',
  }}>
    <div style={{height: 44, overflow: 'hidden'}}>
      <div style={{fontSize: 27, letterSpacing: 4, color: design.accent,
        translate: `${interpolate(local, [0, 12], [-90, 0], {...clamp, easing: ease})}px 0`,
        clipPath: `inset(0 ${interpolate(local, [0, 12], [100, 0], {...clamp, easing: ease})}% 0 0)`,
      }}>{spec.title}</div>
    </div>
    <div style={{color: design.white, scale: interpolate(local, [0, 16], [1.06, 1], {...clamp, easing: ease}), transformOrigin: 'left center'}}>
      <AnimatedCounter value={spec.value} digits={spec.digits} local={local}/>
    </div>
    <svg width="630" height="22" style={{display: 'block', overflow: 'visible'}}>
      <path d="M0 11 H630" stroke="rgba(245,247,244,.25)" strokeWidth="1"/>
      <path d="M0 11 H630" stroke={design.accent} strokeWidth="4" strokeDasharray="630" strokeDashoffset={interpolate(local, [3, 18], [630, 0], {...clamp, easing: ease})}/>
      <rect x={interpolate(local, [3, 18], [0, 620], {...clamp, easing: ease})} y="6" width="10" height="10" fill={design.accent}/>
    </svg>
    <div style={{height: 48, overflow: 'hidden', marginTop: 7}}>
      <div style={{fontSize: 28, letterSpacing: 2,
        translate: `0 ${interpolate(local, [6, 18], [55, 0], {...clamp, easing: ease})}px`,
      }}>{spec.unit}</div>
    </div>
  </div>;
};

export const MotionGraphics = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const time = frame/fps;
  const spec = specifications.find(s => time >= s.start && time < s.end);
  const modelFrame = frame-2.8*fps;
  return <>
    {time >= 2.8 && time < 4.65 && <div style={{position: 'absolute', left: 90, top: 210, width: 830, overflow: 'hidden', opacity: interpolate(time, [4.4,4.65], [1,0], clamp)}}>
      <div style={{fontSize: 76, letterSpacing: '-3px', translate: `0 ${interpolate(modelFrame,[0,14],[100,0],{...clamp,easing:ease})}px`}}>ZEEKR 9X</div>
      <div style={{fontSize: 43, color: design.accent, letterSpacing: 9, translate: `${interpolate(modelFrame,[5,19],[-150,0],{...clamp,easing:ease})}px 0`}}>HYPER</div>
    </div>}
    {spec && <SpecificationOverlay spec={spec}/>}
  </>;
};

export const MainComposition = () => <AbsoluteFill style={{background: '#080B0A', color: design.white, fontFamily: design.fontFamily, fontWeight: 900}}>
  <VideoBackground/>
  <AbsoluteFill style={{background: 'linear-gradient(0deg, rgba(0,0,0,.22), transparent 33%)', pointerEvents: 'none'}}/>
  <MotionGraphics/><AnimatedSubtitles/><AudioLayer/>
</AbsoluteFill>;
export const StyleTest = () => {
  const {fps} = useVideoConfig();
  return <Sequence name="Тест: мощность, моторы, разгон" trimBefore={13.8*fps} durationInFrames={5.9*fps} premountFor={fps}><MainComposition/></Sequence>;
};
