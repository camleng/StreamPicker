#!/usr/bin/env python3

import json
import os
import tkinter as tk
from io import BytesIO
from tkinter import simpledialog, messagebox
import subprocess
import sys

import requests
from PIL import ImageTk, Image
import authentication


class StreamPicker(tk.Frame):
    def __init__(self, master, access_token):
        tk.Frame.__init__(self, master=master)
        self.row = 0
        self.column = 0
        self.base_url = 'https://api.twitch.tv/kraken'
        self.oauth_token = access_token
        self.frames = []
        self.streams = []

        viewer_im = Image.open(os.path.dirname(__file__) + '/viewer.png')
        viewer_im.thumbnail((15, 15))
        self.viewer_img = ImageTk.PhotoImage(viewer_im)

        self.create_menus()

        self.manage_streams()

        self.set_geometry()

    def build_popup_menu(self, channel):
        popup = tk.Menu(root, tearoff=0)
        popup.add_command(label='source', command=lambda: self.open_stream(channel, 'source'))
        popup.add_command(label='high', command=lambda: self.open_stream(channel, 'high'))
        popup.add_command(label='medium', command=lambda: self.open_stream(channel, 'medium'))
        popup.add_command(label='low', command=lambda: self.open_stream(channel, 'low'))
        popup.add_command(label='mobile', command=lambda: self.open_stream(channel, 'mobile'))

        return popup

    def do_popup(self, popup, event):
        popup.tk_popup(event.x_root, event.y_root, 0)

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
        live_streams = self.get_live_streams()['streams']
        if live_streams:
            self.extract_live_streams(live_streams)
        else:
            tk.Label(root, text='No streams available').pack()

    def get_live_streams(self):
        url = '{}/streams/followed?oauth_token={}'.format(self.base_url, self.oauth_token)
        r = requests.get(url)
        live_streams = json.loads(r.text)

        return live_streams

    def extract_live_streams(self, streams):
        for stream in streams:
            display_name = stream['channel']['display_name']
            preview_url = stream['preview']['medium']
            viewer_count = stream['viewers']
            partner = stream['channel']['partner']
            title = stream['channel']['status']

            response = requests.get(preview_url)
            preview_im = Image.open(BytesIO(response.content))
            preview_im.thumbnail((250, 260))

            preview_img = ImageTk.PhotoImage(preview_im)

            if self.column >= 3:
                self.column = 0
                self.row += 1
            self.display_stream_option(display_name, viewer_count, preview_img, title, partner=partner)
            self.column += 1

    def display_stream_option(self, channel, viewers, img, title, partner=False):
        """Add stream to grid
        :param channel
        :param viewers
        :param img
        """
        stream_frame = tk.Frame(self.master)
        self.frames.append(stream_frame)
        stream_frame.configure(background='gray15')

        cursor = 'pointinghand' if sys.platform=='darwin' else 'hand2'
        thumbnail = tk.Label(stream_frame, image=img, cursor=cursor)
        thumbnail.image = img
        thumbnail.bind('<Button-1>', lambda e: self.open_stream(channel))
        CreateToolTip(thumbnail, text=title)
        if partner:
            popup = self.build_popup_menu(channel)
            thumbnail.bind('<Button-2>', lambda e: self.do_popup(popup, e))

        channel_label = tk.Label(stream_frame, text=channel, fg='bisque', bg='gray15')
        viewer_label = tk.Label(stream_frame, text=viewers, image=self.viewer_img, compound=tk.LEFT,
                                fg='bisque', bg='gray15')

        thumbnail.grid(sticky='N')
        channel_label.grid(row=1, sticky='W')
        viewer_label.grid(row=1, sticky='E')
        stream_frame.grid(row=self.row, column=self.column, padx=20, pady=20)

    @staticmethod
    def open_stream(channel, quality='source'):
        """Open stream in VLC
        :param channel
        """
        if '.tv/' in channel.lower():
            # then 'channel' is actually the 'url'. Let's fix that
            url = channel
            channel = url.split('/')[1]
        else:
            url = 'twitch.tv/' + channel

        if sys.platform == 'win32': # Windows
            command = 'start /B livestreamer {} {}'.format(url, quality)
        else: # UNIX
            count = subprocess.check_output('screen -ls | grep {} | wc -l'.format(channel), shell=True)
            if int(count) >= 1:  # another instance running -- don't open
                return
            command = '/usr/local/bin/livestreamer {} {} 2>&1>/dev/null &'.format(url, quality)

        try:
            os.system(command)
        except Exception as e:
            messagebox.showinfo('StreamPicker', e)

    def show_open_stream_dialog(self, service):

        channel = simpledialog.askstring('StreamPicker', service + '.tv/')
        url = '{}.tv/{}'.format(service, channel)
        self.open_stream(url)

    def refresh(self):
        for frame in self.frames:
            frame.grid_forget()

        self.frames.clear()

        self.row = 0
        self.column = 0
        self.manage_streams()
        self.set_geometry()

    def set_geometry(self):
        if self.row == 0:
            width = self.column*295
        elif self.row >= 1 or self.column >= 3:
            width = 3*295
        elif self.column == 2:
            width = 2*295
        else:
            width = (self.column+1) * 295

        height = (self.row+1) * 205
        root.geometry('{}x{}'.format(width, height))


class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.widget.bind('<Enter>', self.enter)
        self.widget.bind('<Leave>', self.close)
        self.tw = None

    def enter(self, event=None):
        x = 0
        y = 0
        x, y, cx, cy = self.widget.bbox('insert')
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry('+{}+{}'.format(x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                       background='#ffffe6', relief='solid', borderwidth=1,
                       font=('times', '8', 'normal'))
        label.pack(ipadx=1)

    def close(self, event=None):
        if self.tw:
            self.tw.destroy()


if __name__ == '__main__':
    token_file = os.path.dirname(__file__) + '/.token'
    if os.path.exists(token_file):
        with open(token_file) as infile:
            access_token = infile.read()
    else:
        access_token = authentication.authenticate_user()
        with open(token_file, 'w') as outfile:
            outfile.write(access_token)

    root = tk.Tk()
    app = StreamPicker(root, access_token)
    root.title('Stream Picker')
    root.configure(background='gray15')
    root.geometry('+{}+{}'.format(210, 150))
    root.mainloop()
