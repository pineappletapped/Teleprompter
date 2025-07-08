# Teleprompter

This repo now provides a fully static HTML/JavaScript teleprompter application that can be hosted on basic shared web hosting without any server side code.

Features include:

- Local registration and login stored in `localStorage`
- Save up to **20 scripts per user**
- Teleprompter page with microphone or auto‑scroll modes
- Simple "Live Session" that syncs text between an input page and a display page using browser storage

## Usage

Simply upload all HTML and JS files to your hosting account. Open `index.html` in your browser to register a user and start creating scripts.

### Live Sessions

To start a live session open `live_input.html` and share the generated link with another device that loads `live_display.html`. Updating the text input will update the display page for any open browser tabs on the same origin.

No server is required, but the live session will only work for clients served from the same domain.
