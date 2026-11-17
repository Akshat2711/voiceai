"""Hexa / Vassi - voice assistant powered by Google Gemini.

Setup and usage: see README.md. Secrets and contacts live in apikey.py
(copy apikey.example.py to apikey.py; it is git-ignored).
"""
import datetime
import io
import os
import smtplib
from email.message import EmailMessage

import mysql.connector as mycon
import pyautogui
import pyttsx3
import pywhatkit as pwk
import speech_recognition as sr
from google import genai
from google.genai import types
from PIL import Image
from win11toast import toast

import apikey as cfg

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODE_FILE = os.path.join(BASE_DIR, "mode.txt")      # "on" = muted, "off" = voice replies
ALARM_SOUND = os.path.join(BASE_DIR, "alarm.mp3")
IMAGE_FILE = os.path.join(BASE_DIR, "vaiimg.png")
WAKE_WORD = "hexa"

TEXT_MODEL = "gemini-2.5-flash"
IMAGE_MODEL = "gemini-2.5-flash-image"
SMTP_HOST, SMTP_PORT = "smtp.gmail.com", 587

recognizer = sr.Recognizer()


# ---------------------------------------------------------------- Gemini API
_client = None


def get_client():
    global _client
    if _client is None:
        if not cfg.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is empty in apikey.py")
        _client = genai.Client(api_key=cfg.GEMINI_API_KEY)
    return _client


def ask_gemini(prompt, grounded=False):
    """Return the model's text, or None if the call failed.
    grounded=True lets Gemini use Google Search for live info (weather, news)."""
    config = None
    if grounded:
        config = types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())])
    try:
        resp = get_client().models.generate_content(
            model=TEXT_MODEL, contents=prompt, config=config)
        return (resp.text or "").strip() or None
    except Exception as e:
        print("Gemini text error:", e)
        return None


def generate_image(prompt):
    """Generate an image with Gemini, save it, and return its path (or None)."""
    try:
        resp = get_client().models.generate_content(model=IMAGE_MODEL, contents=prompt)
    except Exception as e:
        print("Gemini image error:", e)
        return None
    for cand in resp.candidates or []:
        content = cand.content
        for part in (content.parts or []) if content else []:
            if part.inline_data and part.inline_data.data:
                Image.open(io.BytesIO(part.inline_data.data)).save(IMAGE_FILE)
                return IMAGE_FILE
    print("Gemini returned no image")
    return None


# ------------------------------------------------------------ input / output
def is_muted():
    try:
        with open(MODE_FILE, "r") as f:
            return f.read().strip() == "on"
    except OSError:
        return False


def set_mute(on):
    with open(MODE_FILE, "w") as f:
        f.write("on" if on else "off")


def speak(text, rate=170):
    print(text)
    if is_muted():
        return
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", rate)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print("speech output error:", e)


def notify(*lines):
    text = " ".join(str(x) for x in lines)
    print(text)
    try:
        toast(*[str(x) for x in lines])
    except Exception as e:
        print("notification error:", e)


def listen(timeout=None, phrase_limit=None):
    """Record one utterance and return the recognised text, or None."""
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=timeout,
                                      phrase_time_limit=phrase_limit)
    except sr.WaitTimeoutError:
        return None
    try:
        return recognizer.recognize_google(audio).strip()
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        print("speech service error:", e)
        return None


def play_file(path):
    if hasattr(os, "startfile"):   # Windows
        os.startfile(path)
    else:
        print("cannot play", path)


# ------------------------------------------------------------------ database
_db = None


def get_db():
    global _db
    if _db is None or not _db.is_connected():
        _db = mycon.connect(host=cfg.DB_HOST, user=cfg.DB_USER,
                            password=cfg.DB_PASSWORD, database=cfg.DB_NAME)
    return _db


def run_sql(sql, params=None, fetch=False):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(sql, params)
        if fetch:
            return cur.fetchall()
        conn.commit()
    finally:
        cur.close()


# -------------------------------------------------------- helpers
def digits_to_time(text):
    """'7' -> '07:00', '730' -> '07:30', '1430' -> '14:30'. None if invalid."""
    d = "".join(c for c in text if c.isdigit())
    if len(d) == 1:
        h, m = d, "00"
    elif len(d) == 2:
        h, m = d, "00"
    elif len(d) == 3:
        h, m = d[0], d[1:]
    elif len(d) == 4:
        h, m = d[:2], d[2:]
    else:
        return None
    if int(h) > 23 or int(m) > 59:
        return None
    return f"{int(h):02d}:{m}"


def last_word(text):
    return text.strip().split()[-1].lower().strip(".,?!") if text.strip() else ""


def send_email(to_addr, subject, body):
    msg = EmailMessage()
    msg["From"] = cfg.SMTP_EMAIL
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.set_content(body)
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(cfg.SMTP_EMAIL, cfg.SMTP_PASSWORD)
        server.send_message(msg)


# ------------------------------------------------------ scheduled checks
_last_checked_minute = None


def check_alarms_and_reminders():
    """Runs once per minute: fires alarms and reminders that match now."""
    global _last_checked_minute
    now = datetime.datetime.now().strftime("%H:%M")
    if now == _last_checked_minute:
        return
    _last_checked_minute = now

    for (when,) in run_sql("select time from alarm", fetch=True):
        if str(when)[:5] == now:
            notify("Alarm", "ringing...")
            if not is_muted():
                play_file(ALARM_SOUND)

    for topic, when in run_sql("select topic, time from reminder", fetch=True):
        if str(when)[:5] == now:
            notify("Reminder", topic)
            speak("reminder")


# ------------------------------------------------------------ commands
def handle_command(text):
    t = text.lower()

    if "delete all alarm" in t:
        run_sql("delete from alarm")
        speak("all alarms deleted")

    elif "delete all reminder" in t:
        run_sql("delete from reminder")
        speak("all reminders deleted")

    elif "mute mode on" in t:
        set_mute(True)
        notify("mute mode activated")

    elif "mute mode off" in t:
        set_mute(False)
        speak("mute mode deactivated")
        notify("mute mode deactivated")

    elif "temperature" in t:
        place = last_word(text)
        answer = ask_gemini(
            f"What is the current temperature in {place} right now? "
            "Answer in one short sentence with the number in Celsius.",
            grounded=True)
        notify(answer or f"sorry, I couldn't get the temperature for {place}")
        if answer:
            speak(answer)

    elif "today's news" in t or "headlines" in t:
        news = ask_gemini(
            "Give today's top 5 news headlines, one per line, "
            "no numbering and no extra text.", grounded=True)
        if news:
            speak("Here are today's headlines. " + news.replace("\n", ". "), rate=150)
            notify(news)
        else:
            notify("sorry, couldn't fetch the news")

    elif "take screenshot" in t:
        path = os.path.join(BASE_DIR, datetime.datetime.now().strftime("screenshot_%Y%m%d_%H%M%S.png"))
        pyautogui.screenshot(path)
        notify("screenshot saved as:", path)

    elif "text message" in t:
        name = last_word(text)
        phone = cfg.CONTACTS_WHATSAPP.get(name)
        if not phone:
            notify(f"no WhatsApp contact named {name}")
            return
        speak("what's the message")
        message = listen(timeout=8, phrase_limit=20)
        if not message:
            notify("no message heard")
            return
        notify("sending to", name, ":", message)
        pwk.sendwhatmsg_instantly(phone, message, wait_time=15, tab_close=True)
        speak("message sent")

    elif "remind" in t:
        when = digits_to_time(t)
        if not when:
            notify("sorry, I couldn't get the time, try again")
            return
        run_sql("insert into reminder(topic, time) values (%s, %s)", (text, when))
        notify("reminder set for", when)

    elif "create alarm" in t:
        speak("for what time?")
        answer = listen(timeout=8, phrase_limit=6)
        when = digits_to_time(answer or "")
        if not when:
            notify("sorry, I couldn't get the time, try again")
            return
        run_sql("insert into alarm(time) values (%s)", (when,))
        notify("alarm set for", when)
        speak("alarm created")

    elif "what's the time" in t or "what is the time" in t:
        now = datetime.datetime.now().strftime("%H:%M")
        notify("currently it's", now)
        speak(f"currently it's {now}")

    elif "create image" in t:
        notify("generating image...")
        path = generate_image(text)
        if path:
            notify("image saved as", path)
            Image.open(path).show()
        else:
            notify("sorry, image generation failed")

    elif "play" in t.split():
        query = text[text.lower().index("play") + 4:].strip()
        if query:
            pwk.playonyt(query)
        else:
            notify("what should I play?")

    elif "email" in t:
        name = last_word(text)
        to_addr = cfg.CONTACTS_EMAIL.get(name)
        if not to_addr:
            notify(f"no email contact named {name}")
            return
        speak("do you want to use gemini to write the email?")
        choice = listen(timeout=6, phrase_limit=4) or ""
        if "yes" in choice.lower():
            speak("what is the topic of your email?")
            topic = listen(timeout=8, phrase_limit=20)
            if not topic:
                notify("no topic heard")
                return
            body = ask_gemini(
                f"Write a short, polite email to {name}. Topic: {topic}. "
                f"Sign it as {cfg.SENDER_NAME}. Return only the email body.")
            if not body:
                notify("sorry, couldn't write the email")
                return
            notify("draft:", body)
            speak("is it okay? say yes to send")
            confirm = listen(timeout=8, phrase_limit=4) or ""
            if "yes" not in confirm.lower():
                notify("email not sent")
                speak("email not sent")
                return
            subject = topic[:80]
        else:
            speak("ok, tell me what to send")
            body_text = listen(timeout=10, phrase_limit=60)
            if not body_text:
                notify("no message heard")
                return
            body = f"Dear {name},\n{body_text}\n\nRegards,\n{cfg.SENDER_NAME}\n(sent using vassi)"
            subject = "Message"
        try:
            send_email(to_addr, subject, body)
            notify("email sent to:", to_addr)
            speak("email sent")
        except Exception as e:
            print("email error:", e)
            notify("sorry, the email could not be sent")

    else:
        answer = ask_gemini(f"{text}\n\nAnswer briefly in 2-3 sentences.")
        if answer:
            notify(answer)
            speak(answer)
        else:
            speak("sorry, try again")


# ---------------------------------------------------------------- main loop
def main():
    notify("Assistant", f"started. say '{WAKE_WORD}' to begin")
    while True:
        try:
            check_alarms_and_reminders()
        except Exception as e:
            print("alarm/reminder check failed:", e)

        heard = listen(timeout=3, phrase_limit=5)
        if not heard or WAKE_WORD not in heard.lower():
            continue

        speak("yes")
        notify("go ahead, ask your query")
        query = listen(timeout=8, phrase_limit=20)
        if not query:
            speak("sorry, I didn't catch that")
            continue
        print("you said:", query)
        try:
            handle_command(query)
        except Exception as e:
            print("command error:", e)
            speak("sorry, try again")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("bye")
