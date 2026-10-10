import {Composition} from 'remotion';
import {MainComposition, StyleTest} from './Automotive';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition id="StyleTest" component={StyleTest} durationInFrames={177} fps={30} width={1080} height={1920}/>
      <Composition id="AutomotiveReel" component={MainComposition} durationInFrames={591} fps={30} width={1080} height={1920}/>
    </>
  );
};
