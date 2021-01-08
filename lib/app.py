import time
import streamlink
from gi.repository import Gtk, Gdk, WebKit2 as WebKit, Soup
from vlc import Instance

from .player import VlcPlayer

_GLADE_FILE = "assets/UI.glade"
_STYLE_FILE = "assets/UI.css"

class App:
    def __init__(self, channel, quality='best', cookie_storage=None):
        # Load Glade Structure
        WebKit.WebView()

        if cookie_storage is not None:
            # Set the cookie storage file
            WebKit.WebContext.get_default().get_cookie_manager().set_persistent_storage(cookie_storage, WebKit.CookiePersistentStorage.TEXT)

        # Load Glade Structure
        builder = Gtk.Builder()
        builder.add_from_file(_GLADE_FILE)

        # Load Style
        provider = Gtk.CssProvider()
        provider.load_from_path(_STYLE_FILE)
        Gtk.StyleContext.add_provider_for_screen(
          Gdk.Screen.get_default(),
          provider,
          Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.channel = channel
        self.quality = quality

        # Start Vlc Instance
        self.vlc_instance = Instance("--no-xlib")

        # Get Objects
        self.window = builder.get_object("window1")
        self.main_stack = builder.get_object("mainStack1")
        self.video_container = builder.get_object("videoContainer1")
        self.loading_screen = builder.get_object("loadingScreen1")
        self.vlc_drawing_area = builder.get_object("drawingArea1")
        self.webview = builder.get_object("webview1")
        self.panel = builder.get_object("panel1")

        # Initialize VlcPlayer
        self.vlc_player = VlcPlayer(self.vlc_drawing_area, self.vlc_instance)

        # Connect signals and Events
        self.window.connect("destroy", self.__on_window1_destroy)
        self.window.connect("realize", self.__on_window1_realize)

        self.window.connect("check-resize", self.__on_window1_check_resize)
        self.video_container.connect("check-resize", self.__on_window1_check_resize)
        self.panel.connect("draw", self.__on_window1_check_resize)

        # TODO: Add a the loading screen while staying thread safe
        # self.vlc_player.event_attach('media_length_change', self.__on_media_length_changed)

        self.window.connect("key-press-event", self.__on_panel_key_press)

        self.size = None
        self.show_chat = False
        self.chat_size = 400

        # Show the window
        self.window.show_all()
        self.webview.load_uri('https://www.twitch.tv/embed/{}/chat?darkpopout&parent=stream_client'.format(channel))
        self.main_stack.set_visible_child(self.main_stack.get_child_by_name('streamVideo'))

    def __on_panel_key_press(self, widget, event):
        # Toggle Chat on Star Key press
        if event.keyval == 269025072:
            self.show_chat = not self.show_chat
            self.__update_chat()

    def __on_window1_check_resize(self, event=None, data=None):
        if (self.size is None
                or self.size.width != self.window.get_allocation().width
                or self.size.height != self.window.get_allocation().height):
            self.size = self.window.get_allocation()

            if self.size.width < 1000:
                self.show_chat = False

        self.vlc_player.check_size_change()
        self.__update_chat()

    def __update_chat(self):
        if not self.show_chat or self.chat_size > self.size.width:
            self.webview.hide()

            # Hide the cursor
            cursor = Gdk.Cursor.new_for_display(Gdk.Display.get_default(), Gdk.CursorType.BLANK_CURSOR)
            self.window.get_window().set_cursor(cursor)

        else:
            self.panel.set_position(self.panel.get_allocation().width - self.chat_size)
            self.webview.show()

            # Show the cursor
            cursor = Gdk.Cursor.new_for_display(Gdk.Display.get_default(), Gdk.CursorType.LAST_CURSOR)
            self.window.get_window().set_cursor(cursor)

    def __on_window1_destroy(self, object, data=None):
        Gtk.main_quit()

    def __on_window1_realize(self, widget):
        self.window.fullscreen()

        available_streams = streamlink.streams("https://twitch.tv/{}".format(self.channel))

        if available_streams.get(self.quality) is None:
            print('No stream available for the channel "{}" at the quality "{}"'.format(self.channel, self.quality))
            Gtk.main_quit()

        self.vlc_player.load_media(available_streams[self.quality].url)
        self.vlc_player.play()

        self.__update_chat()

    def release(self):
        self.vlc_player.release()
        self.vlc_instance.release()
