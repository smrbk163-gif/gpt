import {Composition} from 'remotion';
import {MainComposition, StyleTest} from './Automotive';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition id="StyleTest" component={StyleTest} durationInFrames={354} fps={60} width={1080} height={1920}/>
      <Composition id="AutomotiveReel" component={MainComposition} durationInFrames={1184} fps={60} width={1080} height={1920}/>
    </>
  );
};
