# Notes for Installing SQX Runs Logger

*18th July 2026*

I advise you converse with Claude AI (my default) or your preferred AI (ChatGPT, Grok, etc.) to guide you through installing this app. It's a simple process — on your VPS you install Python (two commands) and then this app. See below for example installation steps.

All the code is available at [github.com/kabutza1a/sqxlogger](https://github.com/kabutza1a/sqxlogger). It has documentation there too — a User Guide and a System Specification.

## New to GitHub?

Sign up for a free GitHub account if you don't have one. GitHub is a site where programmers and developers share apps — for free. Really, it's just a set of folders. You can ask an AI assistant to connect to it and get the files you need.

If you want to modify SQX Runs Logger, you can do so yourself or ask an AI to help — but first you'll need either your own local copy or a "fork" in GitHub, so you have your own version in your GitHub account's folders rather than editing someone else's directly.

## Where It Can Run

SQX Runs Logger can run locally on a PC or Mac, or on the web via a VPS.

- **Oracle Cloud Free Tier** gives you a free, always-on small VPS where you can run this app and access it from your browser.
- Since it requires almost no resources, you can alternatively install and run it on any Dev or trading VPS you already have.

A cloud VPS like Oracle's Free Tier is typically a headless Linux box, so you'll talk to it via a terminal window using SSH. Again, ask an AI assistant to walk you through this if it's new to you.

## Example Installation Steps

Anyone can clone the repo and get it running:

```bash
git clone https://github.com/kabutza1a/sqxlogger
cd sqxlogger
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
./start.sh
```

Ask your AI assistant to guide you through any step you're unsure of.
