import vlc

class VlcPlayer:
    def __init__(self, gtk_drawing_area, vlc_instance):
        self.gtk_drawing_area = gtk_drawing_area
        self.vlc_instance = vlc_instance

        self.media_player = None
        self.media = None
        self.playing = False

        # Connect signals
        self.gtk_drawing_area.connect("realize", self.__on_realize)

    def __on_realize(self, data=None):
        # Create the media_player
        self.media_player = self.vlc_instance.media_player_new()

        # Disable default VLC input handle
        self.media_player.video_set_key_input(False)
        self.media_player.video_set_mouse_input(False)

        # Attach the media_player to the GTK Drawing Area
        self.media_player.set_xwindow(self.gtk_drawing_area.get_window().get_xid())

        # Check for actions made before realization
        if self.media:
            self.media_player.set_media(self.media)

        if self.playing:
            self.media_player.play()

        # Connect Events
        event_manager = self.media_player.event_manager()
        event_manager.event_attach(vlc.EventType.MediaPlayerLengthChanged, self.__on_length_changed)

    def __on_length_changed(self, event):
        # WARNING: Because self.gtk_drawing_area is used in check_size_change,
        #          this call might not be thread safe and might cause problems
        #          in the future
        self.check_size_change()

    def check_size_change(self):
        if not self.media_player:
          return

        video_size = self.media_player.video_get_size()
        if video_size[0] == 0:
            return

        # Change the height of the drawing area to match the width of the window
        area_width = self.gtk_drawing_area.get_parent().get_allocation().width
        self.gtk_drawing_area.set_size_request(area_width, area_width * video_size[1] / video_size[0])

    def load_media(self, uri):
        if self.media:
            self.media.release()

        self.media = self.vlc_instance.media_new(uri)

        if self.media_player:
            self.media_player.set_media(self.media)

    def play(self):
        self.playing = True

        if self.media_player:
            self.media_player.play()

    def release(self):
        if self.media_player:
            self.media_player.release()

        if self.media:
            self.media.release()
