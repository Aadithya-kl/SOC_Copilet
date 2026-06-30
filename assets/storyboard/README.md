# SOC Copilot Storyboard Assets

This directory contains the master visual assets for the SOC Copilot scroll-triggered frontend experience.

## Story Progression
The storyboard visualizes a complete incident response lifecycle. It begins with a healthy, steady-state system, transitions into an active cyber threat scenario (infection), and concludes with an AI-driven remediation and return to a purified state. The visual narrative relies on a transition of colors: 
- **Blue**: Healthy, normal operations.
- **Red**: Active threat, breach, anomaly detection.
- **Emerald Green**: AI remediation, recovery, purification.

## Frames
1. **Frame 01 (Steady State)**: The system is operating normally. Network traffic flows smoothly in a cool blue luminous aesthetic.
2. **Frame 02 (Initial Anomaly)**: A subtle shift occurs; a minor, suspicious pattern emerges in the data flow.
3. **Frame 03 (Escalation)**: The anomaly spreads, introducing red accents to signify an escalating threat.
4. **Frame 04 (Breach)**: The threat breaches the perimeter. Red alert states dominate the visual space.
5. **Frame 05 (Infection Spread)**: The infection propagates rapidly across nodes. The wireframe distorts.
6. **Frame 06 (Critical Alert)**: Full systemic compromise is depicted, with harsh reds and chaotic geometry.
7. **Frame 07 (AI Copilot Activation)**: The SOC Copilot initiates. Emerald green nodes begin intercepting the red threats.
8. **Frame 08 (Isolation)**: AI isolates the infected segments. Green barriers form around the red compromised zones.
9. **Frame 09 (Remediation)**: Active neutralization of the threat. The red geometry is actively dismantled by the green AI processes.
10. **Frame 10 (System Recovery)**: The network stabilizes. Green transitions back to a calm, purified state.
11. **Frame 11 (Post-Incident Review)**: Analytical nodes summarize the event in a clean, restored blue/green aesthetic.
12. **Frame 12 (Purified State)**: Complete restoration. The system operates at an elevated security posture, radiating a tranquil blue light.

## Scroll Animation Recommendations
- Implement a scroll-scrubbing mechanism where the user's scroll position dictates the frame progression.
- Use interpolation/crossfading between frames or use the frames as key visual anchors while animating WebGL elements.
- Ensure the scroll mapping is non-linear for dramatic effect (e.g., slowing down during the AI remediation phase).

## Layer Separation Recommendations
- For maximum immersion, these static frames can serve as reference points for a multi-layered WebGL implementation.
- Foreground: UI overlays and critical alerts (HTML/CSS).
- Midground: The primary node network (WebGL/Three.js).
- Background: Atmospheric glow and particle effects.
- Consider extracting specific elements from these frames to create parallax layers if using a 2.5D approach.

## Frontend Implementation Notes
- **Resolution**: All frames are 4K (3840x2160) for maximum fidelity. Implement responsive scaling or focal-point cropping for smaller viewports.
- **Preloading**: Due to the high resolution, ensure all images (or optimized versions) are preloaded before the scroll animation begins to prevent stuttering.
- **Fallbacks**: Provide a simplified, non-scroll-dependent experience for users with reduced motion preferences or low-powered devices.
- **Integration**: Copies of these frames should be placed in `frontend/public/storyboard/` for direct access by the frontend application. Do not modify the master copies in this directory.
