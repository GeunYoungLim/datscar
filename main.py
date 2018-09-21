from remote.command import Receiver
import argparse

import subprocess

def recv_command(vector):
    print(vector)


if __name__ == '__main__':
    args = argparse.ArgumentParser()

    args.add_argument('--stream', type=str, default='127.0.0.1:9000')
    args.add_argument('--control', type=str, default='127.0.0.1:8000')
    args.add_argument('--videoinput', type=str, default='0')

    config = args.parse_args()
    stream_url, stream_port = config.stream.split(':')
    control_url, control_port = config.control.split(':')



    ffmpeg = ['ffmpeg',
              '-r','30',
              '-s', '640x480',
              '-an',
              '-f', 'avfoundation',
              '-i', config.videoinput,
              '-f', 'mpegts',
              'udp://{}:{}'.format(stream_url, stream_port)]
    with subprocess.Popen(ffmpeg) as proc:
        print(proc.args)
        receiver = Receiver(control_url, control_port)
        receiver.set_recv_callback(lambda cmd_obj: print(cmd_obj))
        receiver.connect()
