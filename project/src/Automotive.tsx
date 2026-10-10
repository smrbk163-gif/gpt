import React from 'react';
import {AbsoluteFill, Sequence, staticFile, useCurrentFrame, useVideoConfig, interpolate, spring, Easing} from 'remotion';
import {Video, Audio} from '@remotion/media';
import type {Caption} from '@remotion/captions';
import phrasesData from './phrases.json';
import {design, specifications} from './config';
import './style.css';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
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

export const KineticTypography = ({caption}: {caption: (typeof phrases)[number]}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const begin = caption.startMs / 1000 * fps;
  const end = caption.endMs / 1000 * fps;
  const local = frame - begin;
  const parts = caption.accent ? caption.text.split(caption.accent) : [caption.text];
  return <div style={{
    fontSize: design.subtitleSize, fontWeight: 700, lineHeight: 1.18, letterSpacing: '-1.6px',
    textAlign: 'center', textShadow: '0 3px 15px rgba(0,0,0,.8), 0 1px 3px rgba(0,0,0,.95)',
    opacity: Math.min(interpolate(local, [0, 4], [0, 1], clamp), interpolate(frame, [end-3, end], [1, 0], clamp)),
    translate: `0 ${interpolate(local, [0, design.animationFrames], [14, 0], {...clamp, easing: Easing.out(Easing.cubic)})}px`,
    scale: caption.strong ? 0.97 + 0.03 * spring({frame: local, fps, config: {damping: 22, stiffness: 180}}) : 1,
  }}>{parts[0]}{caption.accent && <span style={{color: design.accent}}>{caption.accent}</span>}{parts[1]}</div>;
};

export const AnimatedSubtitles = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const time = frame / fps * 1000;
  const active = phrases.find(c => time >= c.startMs && time < c.endMs);
  return active ? <div style={{position: 'absolute', bottom: design.subtitleBottom, left: 90, width: design.subtitleWidth}}><KineticTypography caption={active}/></div> : null;
};

export const AnimatedCounter = ({value, digits, local}: {value: number; digits: number; local: number}) => {
  const progress = interpolate(local, [0, 9], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  return <>{(value * progress).toLocaleString('ru-RU', {minimumFractionDigits: digits, maximumFractionDigits: digits})}</>;
};

export const SpecificationOverlay = ({spec}: {spec: (typeof specifications)[number]}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const local = frame - spec.start * fps;
  const end = spec.end * fps;
  return <div style={{position: 'absolute', left: 92, top: 195, width: 660,
    opacity: Math.min(interpolate(local, [0, 7], [0, 1], clamp), interpolate(frame, [end-4, end], [1, 0], clamp)),
    translate: `0 ${interpolate(local, [0, design.animationFrames], [20, 0], {...clamp, easing: Easing.out(Easing.cubic)})}px`,
    textShadow: '0 3px 18px rgba(0,0,0,.75)',
  }}>
    <div style={{fontSize: 25, letterSpacing: 4, color: design.accent}}>{spec.title}</div>
    <div style={{fontSize: 150, fontVariantNumeric: 'tabular-nums', letterSpacing: '-6px', lineHeight: 1.1, marginTop: 8}}><AnimatedCounter value={spec.value} digits={spec.digits} local={local}/></div>
    <div style={{display: 'flex', alignItems: 'center', gap: 20, marginTop: 8}}>
      <svg width="54" height="2"><path d="M0 1 H54" stroke={design.accent} strokeWidth="2" strokeDasharray="54" strokeDashoffset={interpolate(local, [0, 12], [54, 0], clamp)}/></svg>
      <span style={{fontSize: 25, letterSpacing: 3}}>{spec.unit}</span>
    </div>
  </div>;
};

export const MotionGraphics = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const time = frame / fps;
  const spec = specifications.find(s => time >= s.start && time < s.end);
  return <>
    {time >= 2.8 && time < 4.65 && <div style={{position: 'absolute', left: 92, top: 225, fontSize: 45, letterSpacing: 2, opacity: interpolate(time, [2.8, 3.05, 4.4, 4.65], [0, 1, 1, 0], clamp)}}>ZEEKR 9X <span style={{color: design.accent}}>Hyper</span></div>}
    {spec && <SpecificationOverlay spec={spec}/>}
  </>;
};

export const MainComposition = () => <AbsoluteFill style={{background: '#080B0A', color: design.white, fontFamily: design.fontFamily}}>
  <VideoBackground/>
  <AbsoluteFill style={{background: 'linear-gradient(0deg, rgba(0,0,0,.18), transparent 30%)', pointerEvents: 'none'}}/>
  <MotionGraphics/><AnimatedSubtitles/><AudioLayer/>
</AbsoluteFill>;

export const StyleTest = () => {
  const {fps} = useVideoConfig();
  return <Sequence name="Тест: мощность, моторы, разгон" trimBefore={13.8 * fps} durationInFrames={5.9 * fps} premountFor={fps}><MainComposition/></Sequence>;
};
