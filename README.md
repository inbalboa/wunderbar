# Wunderbar

A [BitBar](https://getbitbar.com/) plugin that displays your [Wunderlist](https://wunderlist.com/) tasks right in the Mac menu bar.

Also supports GNOME Shell & [Argos](https://github.com/p-e-w/argos)!

![](https://i.imgur.com/rij855z.png)

![](https://i.imgur.com/lNegXGq.png)

## Instructions

### Installation

#### macOS / BitBar
1. Install the latest version of [BitBar](https://github.com/matryer/bitbar/releases/latest). I recommend to use [Homebrew](https://brew.sh/): run `brew cask install bitbar` in the terminal window.
2. Install Python and dependencies: `brew install python && pip3 install --user -U wunderpy2 keyring`.
3. Install [wunderbar.10m.py](wunderbar.10m.py) to the BitBar plugins folder:
```bash
cd "$(defaults read com.matryer.BitBar pluginsDirectory)" && curl -LO https://github.com/inbalboa/wunderbar/releases/latest/download/wunderbar.10m.py && chmod +x wunderbar.10m.py
```

#### GNOME Shell / Argos
1. Install Argos from the [extension page](https://extensions.gnome.org/extension/1176/argos/).
2. Install dependencies. For Ubuntu: `sudo apt install pip3 zenity && pip3 install --user -U wunderpy2 keyring`.
3. Install [wunderbar.10m.py](wunderbar.10m.py) to the Argos plugins folder:
```bash
cd ~/.config/argos && curl -LO https://github.com/inbalboa/wunderbar/releases/latest/download/wunderbar.10m.py && chmod +x wunderbar.10m.py
```

### Setting up
1. Create new app to get client id and create access token on this [Wunderbar's developer page](https://developer.wunderlist.com/apps/).
2. Start BitBar/Argos, or if already running, click the BitBar menu and choose Preferences -> Refresh all (Argos will find the script itself).
3. Input your client id and access token when Wunderbar asks.
