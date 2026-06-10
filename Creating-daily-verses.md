## 1. Creating the Plugin Directory

>❗Currently needs to be updated with how InkyPi has instructed <br>

>❗It is suggested to install cyberduck for ease of plugin updates

```bash
sudo mkdir -p /usr/local/inkypi/src/plugins/daily_verses
cd ~/InkyPi/src/plugins/daily_verses
touch daily_verses.py __init__.py plugin-info.json
```

## 2. Write the plugin code

```bash
sudo nano /usr/local/inkypi/src/plugins/daily_verses/daily_verses.py
```

Input whatever version, code you have

Save by: CTRL+O → Enter

## 3. Creating the metadata

```bash
sudo nano /usr/local/inkypi/src/plugins/daily_verses/plugin-info.json
```

Paste:

```jsx
{
    "display_name": "Daily Verses",
    "id": "daily_verses",
    "class": "DailyVersesPlugin"
}
```