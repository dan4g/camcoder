import PySimpleGUI as sg
import cv2
import os
import datetime

settings = {'fps': 15,
            'resolution_x': 1920,
            'resolution_y': 1080,
            'camera': 0,
            'video_folder': 'videos',
            'name_video': '',
            'running': True,
            'writing': False,
            'preview': '800*450',  # '800*450', '1200*675', '1600*900'
            'auto-focus': 0}


def main_writer_window():
    camera = int(settings['camera'])
    fps = int(settings['fps'])
    name_video = settings['name_video']
    resolution_x = int(settings['resolution_x'])
    resolution_y = int(settings['resolution_y'])

    dim = (int(settings['preview'][0]), int(settings['preview'][1]))

    if not os.path.exists(settings['video_folder']):
        os.makedirs(settings['video_folder'])

    sg.theme('Dark Blue 3')

    writer = cv2.VideoWriter(name_video,
                             cv2.VideoWriter_fourcc(*"MJPG"),
                             fps,
                             (resolution_x, resolution_y))

    layout = [[sg.Image(filename='', key='image', size=(800, 600))],

              [sg.Text('Autofocus'),
               sg.Slider(orientation='h',
                         default_value=0,
                         key='autofocus',
                         range=(0, 1),
                         size=(5, 15))],

              [sg.Text('Focus'),
               sg.Slider(orientation='h',
                         default_value=15,
                         key='focus',
                         range=(0, 255))],

              [sg.Text('Toggle recording'),
               sg.Slider(orientation='h',
                         default_value=settings['auto-focus'],
                         key='recording',
                         range=(0, 1),
                         size=(5, 15))],

              [sg.Button('Make photo')],

              [sg.Button('Exit')]]

    window, cam = sg.Window('OpenCV',
                            layout,
                            location=(0, 0),
                            grab_anywhere=False), cv2.VideoCapture(camera)

    cam.set(3, resolution_x)
    cam.set(4, resolution_y)
    cam.set(cv2.CAP_PROP_AUTOFOCUS, 0)

    writing = 0
    img_count = 0

    while True:

        ret, frame = cam.read()

        if writing == 1.0:
            writer.write(frame)

        window['image'](data=cv2.imencode('.png', cv2.resize(frame, dim))[1].tobytes())
        event, values = window.Read(timeout=(1 / fps))

        if event == 'Exit':
            settings['writing'] = False
            window.close()
            break
        elif event == 'Make photo':
            img_count += 1
            img_name = os.path.join(settings['video_folder'], (str(img_count) + '.jpg'))
            cv2.imwrite(img_name, frame)

        writing = values['recording']

        cam.set(cv2.CAP_PROP_AUTOFOCUS, int(values['autofocus']))
        cam.set(cv2.CAP_PROP_FOCUS, values['focus'])

    writer.release()
    cam.release()

    return settings


def main_menu():
    sg.theme('Dark Blue 3')

    time = str(datetime.datetime.today())[:10] + '-' + str(datetime.datetime.now().time())[:8].replace(':', '-')
    print(time)

    layout = [[sg.Text('Main menu')],

              [sg.Button('Start record')],

              [sg.Text('Enter folder name (document №)'),
               sg.Input(key='document №', default_text='test')],

              [sg.Text('Main video folder'),
               sg.Input(default_text=settings['video_folder'], key='video_folder'),
               sg.FolderBrowse()],

              [sg.Text('')],
              [sg.Text('All setting below to be entered once')],

              [sg.Text('Preview size'),
               sg.Combo(['800*450', '1200*675', '1600*900'], default_value=settings['preview'], key='preview')],

              [sg.Text('Enter FPS'),
               sg.Input(default_text=settings['fps'], key='fps', size=(5, 1))],

              [sg.Text('Enter video resolution'),
               sg.Input(default_text=settings['resolution_x'], key='resolution_x', size=(5, 1)),
               sg.Text(' * '),
               sg.Input(default_text=settings['resolution_y'], key='resolution_y', size=(5, 1))],

              [sg.Text('Enter camera number (do not touch)'),
               sg.Input(default_text=settings['camera'], key='camera', size=(5, 1))],

              [sg.Exit()]]

    window = sg.Window('Main menu', layout)

    while True:
        event, values = window.read()

        if event == 'Exit':
            settings['running'] = False
            window.close()
            break
        elif event == 'Start record':
            settings['preview'] = values.pop('preview').split('*')
            values.pop('Browse')
            doc_n = values.pop('document №')
            settings.update(values)
            settings['video_folder'] = settings['video_folder']
            settings['name_video'] = os.path.join(settings['video_folder'], doc_n, time + '.avi')
            settings['writing'] = True

            print(settings)
            window.close()
            break


while settings['running']:
    main_menu()
    if settings['writing']:
        main_writer_window()
