# Login

### Table of contents <br>
[Image Settings](#image-settings)<br>
[Opening the UI](#opening-the-ui)<br>
[Rebooting InkyPi](#rebooting-inkypi)<br>
[Safe Shutdown](#safe-shutdown)<br>
[Recovery checks after reboot](#recovery-checks-after-reboot)<br>
[Finding the IP address](#finding-the-ip-address)<br>
[Storing API Keys](#storing-api-keys)<br>
[Updating into a branch in Github](#updating-into-a-branch-in-github)<br>
[Forcing a downgrade from a GitHub branch](#forcing-a-downgrade-from-a-github-branch)<br>


As of May 19, 2026

hostname - KloeyInk

username - kloey; password: kloey2002

OS - Raspberry Pi (64-bit)

```bash
ssh <username>@<hostname>.local
```

# Image Settings

- Saturation = 1.8
- Contrast = 1.0
- Sharpness = 1.0
- Brightness = 1.0
- Inky Driver Saturation = 0.2

# Opening the UI

Go to web browser and type http://<hostname>.local

# Rebooting InkyPi

```bash
sudo systemctl daemon-reload
```

# Safe Shutdown

1. Check service:

```bash
systemctl status inkypi
```

Then press q to exit

1. Shutdown:

```bash
sudo shutdown -h now
```

Wait for around 1-2 mins then unplug the power

Keep microSD inserted

Don’t remove it unless replacing or cloning it

# Recovery checks after reboot

Verify service:

```bash
systemctl status inkypi
```

Then press q to exit

Logs:

```bash
journalctl -u inkypi -n 50 --no-pager
```

Open Ui and test the imager

# Finding the IP address

```bash
ping <hostname>.local -4
```

CTRL+C to stop

# Storing API Keys

Repo: https://github.com/fatihak/InkyPi/blob/main/docs/api_keys.md

>❗Use `nano .env` instead


- NASA API: **oH8dsIeJjOddJruZcsYM2Eqd1GapUOtbbsYcSOSD**
    
    Alternative: **Yh7pPgmfpt37QQb1lGbX6BFJ2saKmHEOzC6Kp6dz**
    

# Updating into a branch in Github

```bash
cd /usr/local/inkypi
```

```bash
sudo git fetch origin
sudo git checkout {branch name}
```

branch name e.g. daily-verses-2.0

# Forcing a downgrade from a GitHub branch

```bash
sudo git reset --hard origin/{branch name}
```

```bash
sudo git clean -fd
```

# Checking Git status
```bash
sudo git status
```