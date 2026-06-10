# Troubleshooting the installation

**Table of contents** <br>
[1. Creating Python virtual environment and updating Inkypi](#1-creating-python-virtual-environment-and-updating-inkypi) <br>
[2. Fix PYTHONPATH issue](#2-fix-pythonpath-issue)<br>
[3. Fix hidden import failure](#3-fix-hidden-import-failure)<br>
[4. Restart service and verify logs](#4-restart-service-and-verify-logs)<br>
[5. Opening UI](#5-opening-ui)<br>

### 1. Creating Python virtual environment and updating Inkypi

1. Create a venv:

```bash
python3 -m venv /usr/local/inkypi/venv_inkypi
```

2. Activate:

```bash
source /usr/local/inkypi/venv_inkypi/bin/activate
```

3. Upgrade pip:

```bash
pip install --upgrade pip
```

4. Install Inky library:

```bash
pip install inky pillow
```

5. Deactivate by typing deactivate

### 2. Fix PYTHONPATH issue

1. Edit service:

```bash
sudo nano /etc/systemd/system/inkypi.service
```

2. Add in the service:

```bash
Environment=PYTHONPATH=/home/<username>/InkyPi/src
```

It should look like:

```bash
[Service]

User=kloey
WorkingDirectory=/home/kloey/InkyPi/src

**Environment=PYTHONPATH=/home/kloey/InkyPi/src** 

ExecStart=/usr/local/bin/inkypi run

Restart=always
```

replace the user if needed, it is kloey this instance

Save by pressing: CTRL+O → ENTER → CTRL+X

3. Reload:

```bash
sudo systemctl daemon-reload
```

### 3. Fix hidden import failure

1. Edit:

```bash
nano ~/InkyPi/src/display/display_manager.py
```

2. Replace this whole code:

```python
try:
    from display.inky_display import InkyDisplay
except ImportError:
    logger.info(
        "Inky display not available"
    )
```

with:

```python
from display.inky_display import InkyDisplay
```

You can keep the waveshare section unchanged, since we are using Inky Impression

3. save (CTRL+O → ENTER → CTRL+X)

### 4. Restart service and verify logs

1. Reload:

```bash
sudo systemctl daemon-reload
```

2. Restart:

```bash
sudo systemctl restart inkypi
```

3. Check:

```bash
systemctl status inkypi
```

Expects the return:

```bash
Active: active (running)
```

press q to exit.

4. Verify by running:

```bash
journalctl -u inkypi -n 50 --no-pager
```

5. Expected:

```bash
Starting InkyPi in PRODUCTION mode

Startup flag is set

Displaying image to Inky display

Serving on http://0.0.0.0:80
```

### 5. Opening UI

1. Browser would be: http://<hostname>.local or http://<raspberrypi -ip/
    1. e.g. hostname is kloeypi → http://kloeypi.local
    2. e.g. ip is 192.168.1.172 → http://192.168.1.172

Finding IP

```bash
ping <hostname>.local -4
```

CTRL+C to exit
