# 📅 Day 2 — Linux Fundamentals + My First Bash Script

## 🎯 What is today about?

Today we set up a real Linux environment on a Windows laptop and learned the basic commands that every DevOps engineer uses daily.

We also wrote our very first automation script using AI assistance!

---

## 🏢 How real companies use Linux

| Company | How they use Linux |
|---------|------------------|
| **Google** | Runs all its servers on Linux — including Search, Gmail, YouTube |
| **Amazon AWS** | Every EC2 instance runs Linux by default |
| **Netflix** | Their entire streaming infrastructure runs on Linux |
| **Facebook** | Manages millions of Linux servers using automation |
| **SpaceX** | Runs flight software on Linux |

> 💡 **95% of the world's servers run Linux.** As a DevOps engineer you will work with Linux every single day — no matter which company you join.

---

## 🐧 What is Linux and why does it matter?

Linux is the operating system that runs **95% of the world's servers.**

When you deploy an app to AWS, Google Cloud, or any cloud provider — it runs on Linux. When you work inside Docker containers or Kubernetes — it's Linux underneath.

**As a DevOps engineer, Linux is not optional. It is the foundation of everything.**

---

## 🏗️ Linux Architecture — How it works

```
┌─────────────────────────────────┐
│         Your Application        │  ← The app you deploy
├─────────────────────────────────┤
│         Shell (Bash)            │  ← Where you type commands
├─────────────────────────────────┤
│      System Libraries           │  ← Tools the OS provides
├─────────────────────────────────┤
│         Linux Kernel            │  ← The core brain of Linux
├─────────────────────────────────┤
│           Hardware              │  ← CPU, RAM, Disk, Network
└─────────────────────────────────┘
```

When you type a command in the terminal:
1. Shell receives your command
2. Passes it to the Kernel
3. Kernel talks to hardware
4. Result comes back to your screen

---

## 💻 How to set up Linux on Windows (WSL2)

You don't need a new laptop or dual boot. WSL2 gives you real Linux inside Windows.

**Step 1** — Open PowerShell as Administrator

**Step 2** — Run this one command:
```bash
wsl --install
```

**Step 3** — Restart your computer

**Step 4** — Ubuntu opens automatically. Set a username and password.

**Step 5** — Update your system:
```bash
sudo apt update && sudo apt upgrade -y
```

That's it. You now have real Linux on your Windows machine! 🎉

**💰 Cost:** WSL2 is completely free. No AWS needed for this.

---

## 📋 The 20 Linux commands you must know

These are the commands DevOps engineers use every single day.

### 📁 Moving around
```bash
pwd        # Shows where you are right now
ls         # Lists files and folders
ls -la     # Lists everything including hidden files
cd folder  # Go into a folder
cd ..      # Go back one level
cd ~       # Go to your home folder
```

### 📄 Working with files
```bash
mkdir myfolder          # Create a new folder
touch myfile.txt        # Create an empty file
cp file1.txt file2.txt  # Copy a file
mv file1.txt new.txt    # Rename or move a file
rm myfile.txt           # Delete a file
rm -rf myfolder         # Delete a folder (be careful!)
```

### 👁️ Reading files
```bash
cat filename.txt          # Show file contents
less filename.txt         # Scroll through a file
head -5 filename.txt      # Show first 5 lines
tail -5 filename.txt      # Show last 5 lines
grep "word" filename.txt  # Search for a word in a file
```

### ⚙️ Checking your system
```bash
top       # Live CPU and memory usage (press Q to exit)
df -h     # Check disk space
free -h   # Check RAM usage
whoami    # Shows your current username
uname -a  # Shows system information
```

---

## 🔐 Understanding File Permissions

When you run `ls -la` you see something like this:

```
-rwxr-xr-- 1 root root 1234 system-info.sh
```

**Breaking it down simply:**

```
- rwx r-x r--
│  │   │   │
│  │   │   └── Everyone else: can only read
│  │   └────── Group: can read and run
│  └────────── Owner: can read, write and run
└───────────── - means file / d means folder
```

**The 3 permissions:**
- `r` = read (look at the file)
- `w` = write (change the file)
- `x` = execute (run the file as a program)

**How to change permissions:**
```bash
chmod +x script.sh    # Make a file executable
chmod 755 script.sh   # Owner: full | Others: read and run
```

> 💡 **Beginner tip:** If you see "Permission denied" — fix it with `chmod +x filename`

---

## 🤖 What is a Bash Script?

A Bash script is a **text file full of Linux commands** that run automatically one after another.

| Without a script | With a script |
|-----------------|---------------|
| Type 10 commands manually every time | Run one file, all 10 commands run automatically |
| Easy to make mistakes | Same result every time |
| Takes 5 minutes | Takes 5 seconds |

Think of it like a **recipe** — write the steps once, use them any time.

---

## 📝 Today's Script — system-info.sh

This script shows key information about any Linux system in seconds.

**What it shows:**
- ✅ System hostname (machine name)
- ✅ Current date and time
- ✅ CPU usage percentage
- ✅ Memory (RAM) usage
- ✅ Disk space usage
- ✅ Top 5 running processes

**How to run it:**
```bash
chmod +x system-info.sh
./system-info.sh
```

---

## 🔧 Troubleshooting — common errors and fixes

| Error | Why it happens | Fix |
|-------|---------------|-----|
| `Permission denied` | File is not executable | Run `chmod +x filename.sh` |
| `command not found` | Tool not installed | Run `sudo apt install toolname -y` |
| `No such file or directory` | Wrong path or filename | Run `ls` to check exact filename |
| `chown: invalid user` | Used placeholder text literally | Replace `user` and `group` with real values |
| WSL2 not installing | Windows version too old | Update Windows to version 2004 or higher |
| `bash: ./script.sh: Permission denied` | Script not executable | Run `chmod +x script.sh` first |
| nano won't save | Wrong key combination | Press Ctrl+X → then Y → then Enter |

---

## 🧠 Key Lessons from Day 2

> **Lesson 1:** Linux is not scary. Learn 20 commands and you can work on any server in the world.

> **Lesson 2:** "Permission denied" just means run `chmod +x filename` to fix it.

> **Lesson 3:** A Bash script = automation. Write commands once, run them forever.

> **Lesson 4:** AI can write scripts for you. But always read every line and understand it. That understanding is what makes you a real engineer — not just someone copy-pasting.

> **Lesson 5:** In Linux documentation, words like `user`, `group`, `filename` are placeholders. Always replace them with real values before running.

---

## 🎯 Interview questions — practice these after Day 2

1. **What is the difference between Linux and Windows for servers?**
   > Linux is free, open source, more stable, more secure, and uses fewer resources. 95% of servers run Linux. Windows Server is used mainly in Microsoft-heavy enterprise environments.

2. **What does `chmod 755` mean?**
   > 7 = owner has read+write+execute. 5 = group has read+execute. 5 = everyone else has read+execute. The owner can do everything, others can read and run but not modify.

3. **How do you find which process is using the most CPU?**
   > `top` or `ps aux --sort=-%cpu | head -10` — sorts all processes by CPU usage and shows the top 10.

4. **What is the difference between `rm` and `rm -rf`?**
   > `rm` deletes a single file. `rm -rf` deletes a folder and everything inside it recursively and forcefully. Be very careful with `rm -rf` — it cannot be undone.

5. **How do you search for text inside a file?**
   > Using `grep`. Example: `grep "error" logfile.txt` finds every line containing the word "error". Use `grep -r "error" /var/logs/` to search recursively through all files in a folder.

---

## ❓ Frequently asked questions

**Q: Do I need to buy a Linux machine?**
No! WSL2 gives you real Linux inside Windows for free.

**Q: What if I type a wrong command?**
Most commands are safe. Just avoid `rm -rf` on important folders — that deletes permanently with no undo.

**Q: Why do commands have a `#` after them?**
The `#` starts a comment — it's just a note for humans. Linux ignores everything after `#` on the same line.

**Q: What does `./` mean before a script name?**
It means "run this file from the current folder." Linux needs this to know you want to run a local file.

**Q: What is `sudo`?**
`sudo` means "run this as administrator." Some commands need special permissions — prefix them with `sudo` to get those permissions.

---

## 📚 Resources to go deeper

- [Linux Command Line Basics — Ubuntu](https://ubuntu.com/tutorials/command-line-for-beginners)
- [Bash Scripting Guide](https://www.gnu.org/software/bash/manual/)
- [WSL2 Official Docs](https://learn.microsoft.com/en-us/windows/wsl/)
- [Linux Journey — interactive learning](https://linuxjourney.com/)

---

## 📁 Files in this folder

| File | What it is |
|------|-----------|
| `README.md` | This file — Day 2 complete guide |
| `system-info.sh` | Bash script that displays system information |

---

## ⬅️ Previous Day
[Day 1 — DevOps + AI Fundamentals](../day-01/)

## ➡️ Next Day
[Day 3 — Linux Part 2: Processes, Services, Networking](../day-03/)

---

*Part of my [90-Day DevOps + AI Journey](../../README.md) — documented daily for beginners and professionals alike.*
