# 🤖 MentionBot

A simple Telegram bot for mentioning **group admins** and **active group members**.

## ✨ Features

* 📢 `/admin` — Mention all group admins
* 📣 `/all` — Mention all active users
* 🔄 `@admin` — Mention all admins
* 🔄 `@all` — Mention active users
* 👥 Automatically tracks users who send messages
* 🕐 Mentions users active within the last **15 days**
* 🔐 `/all` is available only to group admins
* 💾 Uses SQLite for user activity tracking

## 📌 Commands

| Command  | Description          |
| -------- | -------------------- |
| `/admin` | Mention all admins   |
| `/all`   | Mention active users |
| `@admin` | Mention all admins   |
| `@all`   | Mention active users |
| `/start` | Show bot information |

## 🗄️ How It Works

The bot automatically tracks users when they send messages in a group.

Users who have been inactive for more than **15 days** are removed from the tracking database.

## 🛠️ Built With

* Python 🐍
* python-telegram-bot 🤖
* SQLite 🗄️

## 👨‍💻 Author

**Angadmaurya9**

⭐ If you find this bot useful, give the repository a star!
