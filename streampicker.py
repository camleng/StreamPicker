import os
import json
import tkinter as tk
from io import BytesIO
from tkinter import simpledialog, messagebox
from threading import Thread

import requests
from PIL import ImageTk, Image


class Stream:
    def __init__(self, display_name, preview_url, viewer_count):
        self.display_name = display_name
        self.preview_url = preview_url
        self.viewer_count = viewer_count
        self.preview_img = None


class StreamPicker(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master=master)
        self.row = 0
        self.column = 0
        self.base_url = 'https://api.twitch.tv/kraken'
        self.oauth_token = 'zk5z17f88iqq347yn63rpbubtadumd'
        self.frames = []
        self.all_streams = []

        viewer_im = Image.open(os.path.dirname(__file__) + '/viewer.png')
        viewer_im.thumbnail((15, 15))
        self.viewer_img = ImageTk.PhotoImage(viewer_im)

        self.create_menus()

        self.manage_streams()

        self.set_geometry()

    def create_menus(self):
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        action_menu = tk.Menu(menubar)

        open_stream_menu = tk.Menu(action_menu)
        open_stream_menu.add_command(label='Twitch', command=lambda: self.show_open_stream_dialog('Twitch'))
        open_stream_menu.add_command(label='MLG', command=lambda: self.show_open_stream_dialog('MLG'))
        open_stream_menu.add_command(label='Azubu', command=lambda: self.show_open_stream_dialog('Azubu'))
        action_menu.add_cascade(label='Open Stream', menu=open_stream_menu)

        action_menu.add_separator()
        action_menu.add_command(label='Refresh', command=self.refresh)
        menubar.add_cascade(label='Actions', menu=action_menu)

    def manage_streams(self):
        live_streams = self.get_live_streams()

        if live_streams:
            streams = live_streams['streams']
            self.extract_live_streams(streams)

    def get_live_streams(self):
        r = requests.get('{}/streams/followed?oauth_token={}'.format(self.base_url, self.oauth_token))
        live_streams = json.loads(r.text)

        return live_streams

    @staticmethod
    def get_preview_img(stream):
        response = requests.get(stream.preview_url)
        print('got image for ' + stream.display_name)
        preview_im = Image.open(BytesIO(response.content))
        preview_im.thumbnail((250, 260))
        stream.preview_img = ImageTk.PhotoImage(preview_im)

    def extract_live_streams(self, streams):
        if not streams:
            tk.Label(root, text='No streams available').pack()

        for stream in streams:
            display_name = stream['channel']['display_name']
            preview_url = stream['preview']['large']
            viewer_count = stream['viewers']
            self.all_streams.append(Stream(display_name, preview_url, viewer_count))

        threads = []
        for stream in self.all_streams:
            t = Thread(target=self.get_preview_img(stream))
            t.start()
            threads.append(t)

        for thread in threads:
            thread.join()

        for stream in self.all_streams:
            if self.column >= 3:
                self.column = 0
                self.row += 1
            self.display_stream_option(stream.display_name, stream.viewer_count, stream.preview_img)
            self.column += 1

        self.all_streams.clear()
        threads.clear()





    def display_stream_option(self, channel, viewers, img):
        """Add stream to grid
        :param channel
        :param viewers
        :param img
        """
        stream_frame = tk.Frame(self.master)
        self.frames.append(stream_frame)
        stream_frame.configure(background='gray15')

        thumbnail = tk.Label(stream_frame, image=img, cursor='pointinghand')
        thumbnail.image = img
        thumbnail.bind('<Button-1>', lambda e: self.open_stream(channel))

        channel_label = tk.Label(stream_frame, text=channel, fg='bisque', bg='gray15')
        viewer_label = tk.Label(stream_frame, text=viewers, image=self.viewer_img, compound=tk.LEFT,
                                fg='bisque', bg='gray15')

        thumbnail.grid(sticky='N')
        channel_label.grid(row=1, sticky='W')
        viewer_label.grid(row=1, sticky='E')
        stream_frame.grid(row=self.row, column=self.column, padx=20, pady=20)

    @staticmethod
    def open_stream(channel):
        """Open stream in VLC
        :param channel
        """
        if '.tv/' in channel.lower():
            # then 'channel' is actually the 'url'. Let's fix that
            url = channel
            channel = url.split('/')[1]
        else:
            url = 'twitch.tv/' + channel

        command = 'screen -d -m -S {} /usr/local/bin/livestreamer {} best'.format(channel, url)
        try:
            os.system(command)
        except Exception as e:
            messagebox.showinfo('StreamPicker', e)

    def show_open_stream_dialog(self, service):
        # open_stream_dialog = tk.Toplevel(root, bg='gray15')
        # open_stream_dialog.geometry('250x50+300+150')
        # label = tk.Label(open_stream_dialog, text=service + '.tv/', fg='bisque', bg='gray15')
        # entry = tk.Entry(open_stream_dialog, fg='bisque', bg='gray15')
        # button = tk.Button(open_stream_dialog, text='Open', bg='gray15',
        #                    command=lambda: self.open_nontwitch_stream(service, entry.get(), open_stream_dialog))
        # label.grid(row=1, column=0)
        # entry.grid(row=1, column=1)
        # button.grid(row=2, column=1)

        channel = simpledialog.askstring('StreamPicker', service + '.tv/')
        url = '{}.tv/{}'.format(service, channel)
        self.open_stream(url)

    # def open_nontwitch_stream(self, service, channel, open_stream_dialog):
    #     url = '{}.tv/{}'.format(service, channel)
    #     open_stream_dialog.forget()
    #     self.open_stream(url)

    def refresh(self):
        for frame in self.frames:
            frame.grid_forget()

        self.frames.clear()

        self.row = 0
        self.column = 0
        self.manage_streams()
        self.set_geometry()

    def set_geometry(self):
        if self.row >= 1 or self.column >= 3:
            width = 3*295
        elif self.column == 2:
            width = 2*295
        else:
            width = (self.column+1) * 295

        height = (self.row+1) * 205
        root.geometry('{}x{}'.format(width, height))

if __name__ == '__main__':
    root = tk.Tk()
    app = StreamPicker(root)
    root.title('Stream Picker')
    root.configure(background='gray15')
    root.geometry('+{}+{}'.format(210, 150))

    root.mainloop()
