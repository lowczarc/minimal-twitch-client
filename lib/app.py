import time
import streamlink
from gi.repository import Gtk, Gdk, WebKit2 as WebKit, Soup
from vlc import Instance

from .player import VlcPlayer

_GLADE_FILE = "assets/UI.glade"
_STYLE_FILE = "assets/UI.css"

class App:
    def __init__(self, stream, quality='best', cookie_storage=None, platform='twitch'):
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

        self.stream = stream
        self.quality = quality
        self.platform = platform

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
        self.webview.connect("load-changed", self.__on_page_change)

        # TODO: Add a the loading screen at the end of the loading of the video while staying thread safe
        # self.vlc_player.event_attach('media_length_change', self.__on_media_length_changed)

        self.window.connect("key-press-event", self.__on_panel_key_press)

        self.size = None
        self.show_chat = False
        self.chat_size = 400

        # Show the window
        self.window.show()

        if self.platform == 'youtube':
            self.webview.load_uri('https://www.youtube.com/live_chat?v={}&dark_theme=1'.format(stream))
        elif self.platform == 'twitch':
            self.webview.load_uri('https://www.twitch.tv/embed/{}/chat?darkpopout&parent=stream_client'.format(stream))
        else:
            raise Exception('Unrecognized Platform')

    def __on_page_change(self, widget, event):
        if event == WebKit.LoadEvent.FINISHED:
            # TODO: Change the video according to the change in url of the chat to support raids

            self.show_chat = True
            self.__update_chat()
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

        if self.platform == 'youtube':
            available_streams = streamlink.streams("https://www.youtube.com/watch?v={}".format(self.stream))
        elif self.platform == 'twitch':
            available_streams = streamlink.streams("https://twitch.tv/{}".format(self.stream))

        if available_streams.get(self.quality) is None:
            print('No stream available for the stream "{}" at the quality "{}" on "{}"'.format(self.stream, self.quality, self.platform))
            print('Available Streams:')
            for stream in available_streams:
                print('\t{}'.format(stream))

            self.window.close()
            return
        else:
            self.vlc_player.load_media(available_streams[self.quality].url)
            self.vlc_player.play()

        self.__update_chat()

    def release(self):
        self.vlc_player.release()
        self.vlc_instance.release()
