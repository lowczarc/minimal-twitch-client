# 📺 Stream Client

A minimal GTK stream viewer for YouTube and Twitch based on streamlink.

## 🚀 Running the app

### ⚠️ Warning

This project has been made for my personal use and therefore has not been tested in any other environment (Arch Linux with Wayland as display server and sway as wm).

The key to open the chat (keyval 269025072) is the star key of the EU keyboard of my Thinkpad T495. I think this key isn't present on most keyboards, so you might want to change it.

### 📦 Dependencies

You need `Gtk3.0`, `streamlink`, and the `python-vlc` bindings installed.

### ▶️ Run

To use it for a Twitch stream, launch:

```sh
./stream_client TWITCH_CHANNEL_NAME
```

Replace `TWITCH_CHANNEL_NAME` with the name of the Twitch channel you want to watch.

To use it for a YouTube live stream, launch:

```sh
./stream_client YOUTUBE_STREAM_ID -yt
```

Replace `YOUTUBE_STREAM_ID` with the ID of the stream (for example, for `https://www.youtube.com/watch?v=dQw4w9WgXcQ`, it would be `dQw4w9WgXcQ`).

## 📝 License

This project is licensed under the `Do whatever you want to do with it, you can reproduce it in less than an hour even without knowing python GTK and libvlc anyway` license.

## 🙏 Credits

* Code by Lancelot Owczarczak
* Logo play by Alex Muravev from the Noun Project
