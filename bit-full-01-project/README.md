# Bit — full seven-angle edit

15.983 seconds, 1080×1920, 60fps. All four original DJI shots and all three new MOV shots. Music excerpt begins at 4.514s from the supplied slowed funk track. Strong accent cuts at 2, 3, 5, 6, 8 and 12s. Smooth sinusoidal speed remaps; frame blending at slow sections, not optical flow. Short matched center-zoom/blur accents, six original transition swishes. Original camera audio muted; music mixed below full scale.

Two-pass vidstab applied to the three new shots: smoothing=12, maxshift=20px, maxangle=0.012rad, 4% fixed zoom plus a small safety crop. Intentional camera movement retained. Old DJI shots kept without additional stabilization. Final departure shot has a gentler speed ramp and no ending zoom punch.

npm ci && npm run dev — composition BeatEditFull. All seven prepared media files and mixed soundtrack are in public/; each is an independently authored JSX node. Final exported using FFmpeg from the same clips and audio used in Remotion.

Scripts document preprocessing; regeneration needs the original uploads and local path manifests referenced by the scripts. Original uploads and stabilization intermediates are not included in this archive.

To keep downloads compact, the final prepared shot in the ZIP is a lighter H.264 rendition; the final MP4 uses the higher-quality prepared master.
