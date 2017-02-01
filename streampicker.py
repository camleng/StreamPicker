import json
import os
import tkinter as tk
from io import BytesIO
from tkinter import simpledialog, messagebox
import subprocess
import sys
import re

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

        viewer_im = Image.open(os.path.join(os.path.dirname(__file__), 'viewer.png'))
        viewer_im.thumbnail((15, 15))

        self.viewer_img = ImageTk.PhotoImage(viewer_im)

        self.create_menus()

        self.manage_streams()

        self.set_geometry()


    def build_popup_menu(self, url):
        popup = tk.Menu(root, tearoff=0)
        for quality in ['best', 'high', 'medium', 'low', 'mobile', 'audio']:
            popup.add_command(label=quality, command=lambda quality=quality: self.open_stream(url, quality))

        return popup


    def do_popup(self, popup, event):
        popup.tk_popup(event.x_root, event.y_root, 0)


    def create_menus(self):
        """Creates the menu bar and the associated menus
        """
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        action_menu = tk.Menu(menubar)

        open_stream_menu = tk.Menu(action_menu)

        # set command for each service
        for service in ['Twitch', 'MLG', 'Azubu']:
            open_stream_menu.add_command(label=service, command=lambda service=service: self.show_open_stream_dialog(service))

        # menu for opening a stream in another service (or a service you don't follow on Twitch)
        action_menu.add_cascade(label='Open Stream', menu=open_stream_menu)
        action_menu.add_separator()

        # menu for watching Twitch Past Broadcasts
        action_menu.add_command(label='Past Broadcast', command=lambda: self.show_open_stream_dialog('Twitch', True))
        action_menu.add_separator()

        # menu for refreshing the live streams
        action_menu.add_command(label='Refresh', command=self.refresh)

        # adds the menu to the menubar
        menubar.add_cascade(label='Actions', menu=action_menu)


    def manage_streams(self):
        live_streams = self.get_live_streams()
        if live_streams:
            self.extract_live_streams(live_streams['streams'])
        else:
            tk.Label(root, text='No streams available').pack()


    def get_live_streams(self):
        url = f'{self.base_url}/streams/followed'
        headers = {'Authorization': f'OAuth {self.oauth_token}'}
        r = requests.get(url, headers=headers)
        live_streams = json.loads(r.text)

        return live_streams


    def extract_live_streams(self, streams):
        for stream in streams:
            display_name = stream['channel']['display_name']
            preview_url = stream['preview']['medium']
            viewer_count = stream['viewers']
            partner = stream['channel']['partner']
            title = stream['channel']['status']
            url = stream['channel']['url']

            response = requests.get(preview_url)
            preview_im = Image.open(BytesIO(response.content))
            preview_im.thumbnail((250, 260))

            preview_img = ImageTk.PhotoImage(preview_im)

            if self.column >= 3:
                self.column = 0
                self.row += 1
            self.display_stream_option(display_name, viewer_count, preview_img, title, url, partner=partner)
            self.column += 1


    def display_stream_option(self, channel, viewers, img, title, url, partner=False):
        """Add stream to grid
        :param channel
        :param viewers
        :param img
        :param title
        :param url
        :param partner
        """
        stream_frame = tk.Frame(self.master)
        self.frames.append(stream_frame)
        stream_frame.configure(background='gray15')

        cursor = 'pointinghand' if sys.platform=='darwin' else 'hand2'
        thumbnail = tk.Label(stream_frame, image=img, cursor=cursor)
        thumbnail.image = img
        thumbnail.bind('<Button-1>', lambda e: self.open_stream(url))
        CreateToolTip(thumbnail, text=title)
        if partner:
            popup = self.build_popup_menu(url)
            thumbnail.bind('<Button-2>', lambda e: self.do_popup(popup, e))

        channel_label = tk.Label(stream_frame, text=channel, fg='bisque', bg='gray15')
        viewer_label = tk.Label(stream_frame, text=viewers, image=self.viewer_img, compound=tk.LEFT, fg='bisque', bg='gray15')

        thumbnail.grid(sticky='N')
        channel_label.grid(row=1, sticky='W')
        viewer_label.grid(row=1, sticky='E')
        stream_frame.grid(row=self.row, column=self.column, padx=20, pady=20)


    def open_stream(self, url, quality='best', past_broadcast=False):
        """Open stream in VLC
        :param url
        :param quality
        :param past_broadcast
        """
        if sys.platform == 'win32':  # Windows
            command = f'start /B streamlink {url} {quality}'
        else:  # UNIX
            instances = subprocess.check_output(f'screen -ls | grep {url} | wc -l', shell=True)
            if int(instances) >= 1:  # don't open another instance
                return

            if past_broadcast:
                command = f'streamlink {url} {quality} --player-passthrough hls 2>&1>/dev/null &'
            else:
                # Client-ID is livestreamer's Client-ID
                command = f'streamlink {url} {quality} --http-header Client-ID=jzkbprff40iqj646a697cyrvl0zt2m6 2>&1>/dev/null &'

        try:
            os.system(command)
        except Exception as e:
            messagebox.showinfo('StreamPicker', e)


    def show_open_stream_dialog(self, service, past_broadcast=False):
        """Shows the dialog for opening streams in other services (or a past broadcast)
        """
        if past_broadcast:
            url = simpledialog.askstring('StreamPicker', service + '.tv Past Broadcast')
        else:
            channel = simpledialog.askstring('StreamPicker', service + '.tv/')
            url = '{}.tv/{}'.format(service, channel)

        self.open_stream(url, 'best', past_broadcast)


    def refresh(self):
        for frame in self.frames:
            frame.grid_forget()

        self.frames.clear()

        self.row = 0
        self.column = 0
        self.manage_streams()
        self.set_geometry()


    def set_geometry(self):
        """Sets the height and width based on the number of streams that are live
        """
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
    """Create a tooltip for a given widget
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
    # file that contains the access token used for making authenticated calls
    token_file = os.path.join(os.path.dirname(__file__), '.token')

    # read the token file
    if os.path.exists(token_file):
        with open(token_file) as f:
            access_token = f.read().strip()

    # if it's not there, get a new one and save it
    else:
        access_token = authentication.authenticate_user()
        with open(token_file, 'w') as f:
            f.write(access_token)

    root = tk.Tk()
    app = StreamPicker(root, access_token)
    root.title('Stream Picker')
    root.configure(background='gray15')
    root.geometry('+210+150')
    root.mainloop()
