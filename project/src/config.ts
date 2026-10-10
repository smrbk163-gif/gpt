export const design = {
  fontFamily: 'Inter, sans-serif', white: '#F5F7F4', accent: '#C2D991',
  subtitleSize: 60, subtitleBottom: 310, subtitleWidth: 864, animationFrames: 10,
  color: {contrast: 1.025, saturation: 0.96, brightness: 1.025}, soundVolume: 0.16,
};
// Intra-cue timings are provisional; captions.json retains original SRT boundaries.
export const specifications = [
  {start: 13.8, end: 15.88, value: 1401, digits: 0, title: 'МОЩНОСТЬ', unit: 'ЛОШАДИНАЯ СИЛА'},
  {start: 16.08, end: 17.2, value: 3, digits: 0, title: 'СИЛОВАЯ УСТАНОВКА', unit: 'ЭЛЕКТРОМОТОРА'},
  {start: 18.5, end: 19.68, value: 3.1, digits: 1, title: 'РАЗГОН 0–100 КМ/Ч', unit: 'СЕКУНДЫ'},
];
