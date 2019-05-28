import mdl
from display import *
from matrix import *
from draw import *

"""======== first_pass( commands ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)

  Should set num_frames and basename if the frames
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.
  ==================== """
def first_pass( commands ):

    name = ''
    num_frames = 1

    # For ease of manipulation
    basename = False
    vary = False
    frames = False

    for command in commands:
        op = command['op']
        args = command['args']

        if op == 'frames':
            frames = True
            num_frames = args[0]
        if op == 'basename':
            basename = True
            name = args[0]
        if op == 'vary':
            vary = True

    if (vary and not frames):
        exit()

    if (frames and not basename):
        name = 'base'
        print("Using 'base' as default value")

    return (name, num_frames)


"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value.
  ===================="""

def second_pass( commands, num_frames ):
    #array of dictionaries
    #knob[0] first frame
    num_frames= int(num_frames)
    frames = [ {} for i in range(num_frames)]
    #print("commands: "+ str(commands))
    for command in commands:
        op = command['op']
        args = command['args']
        if op == "vary":
            cnt = command['knob']
            firstFrame = int(args[0])
            lastFrame = int(args[1])

            firstVal = args[2]
            lastVal = args[3]

            s = (lastVal-firstVal)/(lastFrame-firstFrame)

            for i in range(firstFrame, lastFrame +1):
                frames[i][cnt] = firstVal + s*(i-firstFrame)

    return frames

def run(filename):
    """
    This function runs an mdl script
    """
    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return

    view = [0,
            0,
            1];
    ambient = [50,
               50,
               50]
    light = [[0.5,
              0.75,
              1],
             [255,
              255,
              255]]

    color = [0, 0, 0]
    symbols['.white'] = ['constants',
                         {'red': [0.2, 0.5, 0.5],
                          'green': [0.2, 0.5, 0.5],
                          'blue': [0.2, 0.5, 0.5]}]
    reflect = '.white'

    (name, num_frames) = first_pass(commands)
    frames = second_pass(commands, num_frames)

    for i in range(int(num_frames)):
        tmp = new_matrix()
        ident( tmp )

        stack = [ [x[:] for x in tmp] ]
        screen = new_screen()
        zbuffer = new_zbuffer()
        tmp = []
        step_3d = 100
        consts = ''
        coords = []
        coords1 = []

        for command in commands:
            print command
            c = command['op']
            args = command['args']
            knob_value = 1

            if "knob" in command.keys() and command['knob'] != None:
                knob_value = frames[i][command['knob']]

            if c == 'box':
                if command['constants']:
                    reflect = command['constants']
                add_box(tmp,
                        args[0]*knob_value, args[1]*knob_value, args[2]*knob_value,
                        args[3]*knob_value, args[4]*knob_value, args[5]*knob_value)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'sphere':
                if command['constants']:
                    reflect = command['constants']
                add_sphere(tmp,
                           args[0]*knob_value, args[1]*knob_value, args[2]*knob_value, args[3]*knob_value, step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'torus':
                if command['constants']:
                    reflect = command['constants']
                add_torus(tmp,
                          args[0]*knob_value, args[1]*knob_value, args[2]*knob_value, args[3]*knob_value, args[4]*knob_value, step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'line':
                add_edge(tmp,
                         args[0]*knob_value, args[1]*knob_value, args[2]*knob_value, args[3]*knob_value, args[4]*knob_value, args[5]*knob_value)
                matrix_mult( stack[-1], tmp )
                draw_lines(tmp, screen, zbuffer, color)
                tmp = []
            elif c == 'move':
                tmp = make_translate(args[0]*knob_value, args[1]*knob_value, args[2]*knob_value)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                tmp = make_scale(args[0] * knob_value, args[1]*knob_value, args[2]*knob_value)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                theta = args[1] * (math.pi/180) * knob_value
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])
        save_extension(screen,"./anim/" + name + ("0000" + str(i))[-4:])
            # end operation loop
