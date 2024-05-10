import numpy as np

screen_size = 40
theta_spacing = 0.07
phi_spacing = 0.02
illumination = np.fromiter(".,-~:;=!*#$@", dtype="<U1")

A = 1
B = 1
R1 = 1
R2 = 2
K2 = 5
K1 = screen_size * K2 * 3 / (8 * (R1 + R2))


def render_frame(A: float, B: float) -> np.ndarray:
    """
    Returns a frame of the spinning 3D donut.
    Based on the pseudocode from: https://www.a1k0n.net/2011/07/20/donut-math.html
    """
    cos_A = np.cos(A)
    sin_A = np.sin(A)
    cos_B = np.cos(B)
    sin_B = np.sin(B)

    output = np.full((screen_size, screen_size), " ")  # (40, 40)
    zbuffer = np.zeros((screen_size, screen_size))  # (40, 40)

    cos_phi = np.cos(phi := np.arange(0, 2 * np.pi, phi_spacing))  # (315,)
    sin_phi = np.sin(phi)  # (315,)
    cos_theta = np.cos(theta := np.arange(0, 2 * np.pi, theta_spacing))  # (90,)
    sin_theta = np.sin(theta)  # (90,)
    circle_x = R2 + R1 * cos_theta  # (90,)
    circle_y = R1 * sin_theta  # (90,)

    x = (np.outer(cos_B * cos_phi + sin_A * sin_B * sin_phi, circle_x) - circle_y * cos_A * sin_B).T  # (90, 315)
    y = (np.outer(sin_B * cos_phi - sin_A * cos_B * sin_phi, circle_x) + circle_y * cos_A * cos_B).T  # (90, 315)
    z = ((K2 + cos_A * np.outer(sin_phi, circle_x)) + circle_y * sin_A).T  # (90, 315)
    ooz = np.reciprocal(z)  # Calculates 1/z
    xp = (screen_size / 2 + K1 * ooz * x).astype(int)  # (90, 315)
    yp = (screen_size / 2 - K1 * ooz * y).astype(int)  # (90, 315)
    L1 = (((np.outer(cos_phi, cos_theta) * sin_B) - cos_A * np.outer(sin_phi, cos_theta)) - sin_A * sin_theta)  # (315, 90)
    L2 = cos_B * (cos_A * sin_theta - np.outer(sin_phi, cos_theta * sin_A))  # (315, 90)
    L = np.around(((L1 + L2) * 8)).astype(int).T  # (90, 315)
    mask_L = L >= 0  # (90, 315)
    chars = illumination[L]  # (90, 315)

    for i in range(90):
        mask = mask_L[i] & (ooz[i] > zbuffer[xp[i], yp[i]])  # (315,)

        zbuffer[xp[i], yp[i]] = np.where(mask, ooz[i], zbuffer[xp[i], yp[i]])
        output[xp[i], yp[i]] = np.where(mask, chars[i], output[xp[i], yp[i]])

    return output

import io

def print_to_string(*args, **kwargs):
    output = io.StringIO()
    print(*args, file=output, **kwargs)
    contents = output.getvalue()
    output.close()
    return contents

def pprint(fn, color, array: np.ndarray) -> None:
    """Pretty print the frame."""
    s = print_to_string(*[" ".join(row) for row in array], sep="\n")
    s_dc = {"string": s, "rgb_color": color}
    fn(s_dc)


def run(terminator, print_func):
    screen_size = 20
    theta_spacing = 0.07
    phi_spacing = 0.02
    illumination = np.fromiter(".,-~:;=!*#$@", dtype="<U1")

    A = 1
    B = 1
    R1 = 1
    R2 = 2
    K2 = 5
    K1 = screen_size * K2 * 3 / (8 * (R1 + R2))

    r = 0
    g = 128
    b = 255
    r_d = 1
    g_d = -1
    b_d = 1

    while not terminator[0]:
        for _ in range(screen_size * screen_size):
            if terminator[0]:
                break

            if r > 248:
                r_d = -1
            if r < 6:
                r_d = 1
            if b > 248:
                b_d = -1
            if b < 6:
                b_d = 1
            if g > 248:
                g_d = -1
            if g < 6:
                g_d = 1
            r += r_d*5
            g += g_d*5
            b += b_d*5
            color_rgb = f"rgb({str(r)}, {str(g)}, {str(b)})"

            A += theta_spacing
            B += phi_spacing
            #print_func("")
            pprint(print_func, color_rgb, render_frame(A, B))