# Hexa (VoiceAI) – Gemini voice assistant

A Windows voice assistant that listens for a wake word and answers questions with
Google Gemini, writes and sends emails, sets alarms and reminders, takes
screenshots, generates images, sends WhatsApp messages, and plays YouTube videos.

## Features

| Say (after the wake word "hexa") | What happens |
|---|---|
| *any question* | Gemini answers briefly (spoken + toast) |
| *what's the temperature in Delhi* | Live temperature via Gemini + Google Search |
| *today's news / headlines* | Top 5 headlines via Gemini + Google Search |
| *create alarm* → then say the time | Saves an alarm; it rings at that time |
| *remind me at 7 to drink water* | Saves a reminder with a toast at that time |
| *delete all alarm / delete all reminder* | Clears the saved alarms or reminders |
| *what's the time* | Speaks the current time |
| *take screenshot* | Saves `screenshot_<date>_<time>.png` in the project folder |
| *create image \<description\>* | Generates an image with Gemini and opens it |
| *play \<song or topic\>* | Opens the search on YouTube |
| *email \<name\>* | Asks whether Gemini should write it, confirms, then sends via Gmail |
| *text message to \<name\>* | Sends a WhatsApp message through WhatsApp Web |
| *mute mode on / mute mode off* | Silences / re-enables spoken replies (state saved in `mode.txt`) |

## Requirements

- Windows 10/11 with a working microphone and speakers
- Python 3.10 or newer
- Internet access (Gemini, Google speech recognition, Google Search grounding)
- MySQL or MariaDB server (for alarms and reminders)
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
- A Gmail account with an [App Password](https://myaccount.google.com/apppasswords) (for sending email)
- WhatsApp Web logged in on the default browser (for WhatsApp messages)

## Setup

1. **Install Python packages**

   ```bash
   pip install -r requirements.txt
   ```

   `PyAudio` can fail to install with plain pip on some Python versions. If it does,
   install a matching wheel or use `pipwin install pyaudio`.

2. **Create the database**

   ```sql
   CREATE DATABASE vassi;
   USE vassi;
   CREATE TABLE alarm (time VARCHAR(5));
   CREATE TABLE reminder (topic VARCHAR(255), time VARCHAR(5));
   ```

3. **Create your config file**

   Copy `apikey.example.py` to `apikey.py` and fill in:
   - `GEMINI_API_KEY`
   - `SMTP_EMAIL` and `SMTP_PASSWORD` (Gmail App Password)
   - `DB_*` values if your MySQL login is not `root` with no password
   - `CONTACTS_WHATSAPP` and `CONTACTS_EMAIL`, keyed by lowercase first name

   `apikey.py` is git-ignored. Keep your keys out of the code and out of git.

4. **Run**

   ```bash
   python voiceai.py
   ```

   Say **"hexa"**, wait for "yes", then ask your query.

## Configuration

- Gemini models are set at the top of `voiceai.py`:
  `TEXT_MODEL = "gemini-2.5-flash"` and `IMAGE_MODEL = "gemini-2.5-flash-image"`.
  Change them if Google renames or retires a model.
- `WAKE_WORD = "hexa"` can be changed in `voiceai.py`.

## Notes and limitations

- Voice recognition uses Google's free web speech API, so it needs internet.
- WhatsApp messages open WhatsApp Web in your browser. You must already be logged in,
  and the browser window will open for a few seconds.
- Alarms and reminders are checked once a minute while the assistant is running.
  Alarms repeat every day until you delete them.
- The alarm sound (`alarm.mp3`) plays only when mute mode is off.
- Screenshots and generated images are saved in the project folder.
- Code is written for Windows (uses win11toast and `os.startfile`).

## Project files

- `voiceai.py` – main assistant
- `apikey.example.py` – template for your private config
- `requirements.txt` – Python dependencies
- `mode.txt` – mute state (`on` / `off`)
- `alarm.mp3` – alarm sound
