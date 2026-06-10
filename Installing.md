# Installing guide
This is a guide on how to install the InkyPi. This is a guide based on the original git repository, but offers more detail and focuses on Raspberry Pi 3 A+

### Table of contents<br>

[1. Download Raspberry Pi imager](#1-download-raspberry-pi-imager)<br>
[2. Booting up Raspberry Pi](#2-booting-up-raspberry-pi)<br>
[3. Cloning InkyPi](#3-cloning-inkypi)<br>
[Cyberduck](#cyberduck)

## 1. Download Raspberry Pi imager
1. Install the Raspberry Pi Imager from the [official download page](https://www.raspberrypi.com/software/)
2. Insert the target SD Card into your computer and launch the Raspberry Pi Imager software
- Device: Choose your Pi model (Raspberry Pi 3).

![Choosing Pi model](/images/choosing%20device.png)

- Operating System: Raspberry Pi OS (Legacy, 64-bit).

![Choosing Pi OS](/images/choosing%20os.png)

- Storage: Select the target SD Card.

3. Customisation:
    1. Set hostname: enter your desired hostname (e.g. kloeypi, InkyFrame)
    > This will be used to ssh into the device & access the InkyPi UI on your network.
    2. Set username & password
    > ❗ Do not use the default username and password on a Raspberry PI as this poses a security risk.<br>
    > ❗Place a simple username, no hyphens or other symbols
    3. Configure wireless LAN to your network
    > The InkyPi web server will only be accessible to devices on this network.
    4. Set local settings to your Time zone
    5. Service:
    - Enable SSH: Use password authentication
    6. Options: leave default values

4. Write on SD Card and then eject when finished

## 2. Booting up Raspberry Pi
1. Plug in SD card and plug power into raspberry pi
    > Wait for 1-2 minutes for the Pi to load
2. Open CMD terminal on Windows
3. Log into the Raspberry Pi:<br>
    ```bash
    ssh username@hostname.local
    ```
    > 💡 For example: <br>
    > username is kloey, hostname is displayer <br>
    > Type: ssh kloey@displayer.local

4. It will ask for the password, you have to type this in but it will be blank. Just finish typing and enter
    - If you fail to type your password 3x it will lock out
    - If you fail or forgot your password, rewrite the OS on the SD card and repeat from step 1.
        - It will prompt to have an issue, but just input:
        ```bash
        ssh-keygen -R <hostname>.local
        ```
        - If it asks “Are you sure you want to continue connecting (yes/no/[fingerprint])?” , type yes and then log in

5. Update system:
    ```bash
    sudo apt update
    ```
    then
    ```bash
    sudo apt full-upgrade -y
    ```

6. Install required packages:
    ```bash
    sudo apt install -y git python3-venv python3-pip python3-full
    ```

7. Reboot
    ```bash
    sudo reboot
    ```

## 3. Cloning InkyPi

1. Clone github:

```bash
cd ~
git clone https://github.com/fatihak/InkyPi.git
```

2 Install Inkypi:

```bash
cd Inkypi
sudo bash install/install.sh
```

- It will ask to reboot, yes
> ❗ If the e-ink screen does not refresh and says the hostname in the middle as a title that means it’s not working. Proceed to [Troubleshooting](Troubleshooting-installation.md)

- You can verify:

```bash
ls /usr/local/inkypi/venv_inkypi/bin/python
```
The return should be: /usr/local/inkypi/venv_inkypi/bin/python


3. Upgrade inky library in venv
First check inky version in cmd
```bash
pip show inky
```
It should have the latest version in the [Pimoroni Inky Github](https://github.com/pimoroni/inky]) in “Releases on the right tab”

If it’s not updated then:
```bash
source /usr/local/inkypi/venv_inkypi/bin/activate
sudo /usr/local/inkypi/venv_inkypi/bin/pip install --upgrade inky
```
or pin explicitly:
```bash
sudo /usr/local/inkypi/venv_inkypi/bin/pip install inky== <lastest version number>
```

4. Verify, it should say ``<class `inky.inky_e673.Inky'>``:
```bash
python -c "
from inky.auto import auto
d=auto()
print(type(d))
"
```
5. Reboot:
```bash
sudo systemctl daemon-reload
sudo systemctl restart inkypi.service
```

## Cyberduck
[Cyberduck](https://cyberduck.io) is a libre server and cloud storage browser for Mac and Windows with support for FTP, SFTP, WebDAV, Amazon S3, OpenStack Swift, Backblaze B2, Microsoft Azure & OneDrive, Google Drive and Dropbox.

It can help provide a visual screen for the raspberry pi files and is recommended especially with plugins and updates