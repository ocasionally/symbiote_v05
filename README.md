<p align="center">
  <b>#TO BE USED IN CONTROLLED ENVIRONMENTS ONLY#<b>
</p>

<p align="center">
Symbiote is a social engineering tool designed to create a phishing page and capture webcam images. By requesting camera permission on the victim's device, this script can take pictures covertly. If you're interested in contributing to the project, we'd love to have you on board.
</p>

---

# SYMBIOTE (educational edition)

Minimal and stable version, adapted to run in **controlled environments**
(e.g. a class lab with authorized participants).

## WHAT'S IN THIS EDITION

- **"Veridia Solutions S.A." corporate landing** (`Server/www_f/index2.html`):
  a fictional corporate site (invented logo, nav, About, Employees directory,
  Contact section) in Spanish, with the identity-verification portal embedded.
  The camera stage is the funnel target of a mandatory security notice
  ("complete before 30 Nov") — reachable in one click from nav, banner or
  `index2.html#verificacion`.
  - **Front camera by default** with front ↔ back switch (auto mirroring).
    The switch button only shows once the camera is running.
- **Back-camera original page** (`Server/www_b/index2.html`).
- **Email notifications**: at startup the tool asks for the sender Gmail
  account + app password (kept in memory only). From the monitor prompt,
  `send <email>` delivers the corporate email template
  (`Server/email_template.html`, `{{LINK}}` replaced with the live ngrok URL)
  via Gmail SMTP.
- **Fraud-support console in English**; page content in Spanish.

## CAPTURE ENGINE

- **Frames every 2.5 s** + a final high-quality selfie, sent to `post.php`.
- **Liveness challenges** (blink / smile / turn head) keep the subject in
  front of the camera.
- **Per-IP folder** in `CapturedData/<IP>/` with `info.txt`:
  - Parsed User-Agent (browser, OS, device type).
  - **IP geolocation** (ip-api.com — 1 cached lookup per IP): country,
    region, city, coordinates, timezone, ISP/AS, connection type
    (mobile / VPN / residential).
  - Browser intel: screen + DPR, orientation, window size, languages,
    CPU cores, approx. RAM, GPU, battery level + charging state, network
    type/downlink/RTT, storage quota, referrer, DNT, cookies.
  - **Conditional GPS**: only if geolocation permission was already granted
    for the domain (silent `permissions.query`); otherwise skipped without
    any visible prompt.
  - `info.txt` is refreshed on every capture (first-capture date and cached
    geo are preserved).

## REQUIREMENTS

* Python 3
* PHP (php-cli)
* ngrok (with your own account; you start it manually)
* (Optional) A Gmail account + app password to use the `send` command

## INSTALLATION

```
sudo apt update
sudo apt install python3 php-cli -y
# ngrok: download from https://ngrok.com and authenticate with your authtoken
```

## USAGE

```
1) python3 symbiote.py   # Enter = consent / camera / port 1516
                         # then: Gmail + app password (ENTER = skip)
2) ngrok http 1516       # in another terminal (or beforehand)
3) ENTER in the monitor  # public URL appears (auto-detected via local API 4040)
   send victim@mail.com  # emails the verification link (Gmail SMTP)
4) X to exit
```

**Important:**

- Run **without sudo** (avoids root-owned files).
- The tool **does not manage ngrok**: it only detects its public URL.
- Camera access requires HTTPS (the tunnel) or localhost.
- GPS is only read if the victim already granted permission for the domain.
- Gmail SMTP needs an **app password** (16 chars, myaccount.google.com/apppasswords);
  regular passwords always fail.
- The template footer states the email is part of an academic exercise in a
  controlled environment.

## CAPTURED DATA

Each victim folder contains the photos (`cam*.png`) and an `info.txt` with the
full session profile (see CAPTURE ENGINE above). `CapturedData/ip.txt`
accumulates the victim IPs detected. Runtime files (`Log.log`, `ip.txt`,
`path.txt`, `link.url`, `CapturedData/`) are git-ignored and never committed.

## LICENSE

MIT — see `LICENSE`. This fork keeps the original project's license
(hasanfirnas/symbiote) and is intended to run only in **controlled
environments** with authorized participants and consent.
