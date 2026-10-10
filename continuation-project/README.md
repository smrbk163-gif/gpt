# ZEEKR 9X Hyper — continuation
19.3667 seconds, 1080×1920, 30fps. Composition: Continuation.

Montserrat Black 900; white and lime #BFFF00; no text shadows. Local animated shading, masked typography, rolling weight digits, animated weight icon, emotional underline, flying Telegram plane. Original cut structure and speech retained; subtle camera movement resets at 5.338667 and 13.86385 seconds. Original seeded sound design.

The supplied SRT has phrase-level timing. Internal phrase splits are editorial estimates, not word-level forced alignment. Original cue boundaries are retained in src/captions.json and public/source.srt. The user approved correcting “rolls-Royce Calin” to “Rolls-Royce Cullinan” in displayed captions. No Telegram handle was supplied; CTA follows the spoken profile-description reference.

Install: npm ci
Preview: npm run dev
Render: npx remotion render src/index.ts Continuation continuation.mp4 --codec=h264 --video-bitrate=4M --audio-codec=aac --audio-bitrate=192k
Regenerate original sounds: python scripts/generate_sfx.py
