import curses
import random
import time

def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_WHITE, -1)
    curses.init_pair(4, curses.COLOR_CYAN, -1)
    curses.init_pair(5, 22, -1)
    curses.init_pair(6, curses.COLOR_BLUE, -1)
    curses.init_pair(7, curses.COLOR_MAGENTA, -1)
    curses.init_pair(8, curses.COLOR_YELLOW, -1)

    sh, sw = stdscr.getmaxyx()
    layers = []
    for depth in range(4):
        cols = [random.randint(-sh * 3, 0) for _ in range(sw)]
        speeds = [random.uniform(0.45, 2.2) * (1.0 + depth * 0.38) for _ in range(sw)]
        layers.append({"cols": cols, "speeds": speeds, "depth": depth})

    chars = (
        "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*+=-<>?█▓▒░"
    )

    logo = [
        r"██╗  ██╗███████╗    ███╗   ███╗ ██████╗ ",
        r"╚██╗██╔╝██╔════╝    ████╗ ████║██╔═══██╗",
        r" ╚███╔╝ █████╗      ██╔████╔██║██║   ██║",
        r" ██╔██╗ ██╔══╝      ██║╚██╔╝██║██║   ██║",
        r"██╔╝ ██╗███████╗    ██║ ╚═╝ ██║╚██████╔╝",
        r"╚═╝  ╚═╝╚══════╝    ╚═╝     ╚═╝ ╚═════╝ ",
    ]

    frame = 0
    intensity = 1.0
    intensity_timer = 0
    glitch_timer = 0
    aurora_offset = 0.0
    shake = 0
    sparks = []

    while True:
        stdscr.erase()
        sh, sw = stdscr.getmaxyx()

        if intensity_timer > 0:
            intensity_timer -= 1
            if intensity_timer <= 0:
                intensity = 1.0
        elif random.random() < 0.009:
            intensity = random.uniform(3.2, 6.8)
            intensity_timer = random.randint(30, 90)
            shake = random.randint(2, 5)

        if shake > 0:
            shake -= 1

        aurora_offset += 0.055 + intensity * 0.012

        y_offset = random.randint(-shake, shake) if shake else 0

        for layer in layers:
            depth = layer["depth"]
            for x in range(min(sw, len(layer["cols"]))):
                y = int(layer["cols"][x]) + y_offset
                trail_len = int((12 - depth * 2.1) * min(intensity, 3.4))

                reverse = intensity > 3.5 and random.random() < 0.04

                for t in range(trail_len):
                    yy = y + t if reverse else y - t
                    if 0 <= yy < sh:
                        try:
                            ch = random.choice(chars)
                            aurora_pos = (x / max(sw, 1) + aurora_offset + yy * 0.008) % 4.0
                            if aurora_pos < 1.0:
                                base = 1
                            elif aurora_pos < 2.0:
                                base = 4
                            elif aurora_pos < 3.0:
                                base = 6
                            else:
                                base = 7

                            if t == 0:
                                attr = curses.color_pair(2) | curses.A_BOLD
                                if random.random() < 0.14 * intensity:
                                    attr = curses.color_pair(3) | curses.A_BOLD
                                elif random.random() < 0.05 * intensity:
                                    attr = curses.color_pair(8) | curses.A_BOLD
                            elif t < 3:
                                attr = curses.color_pair(base) | curses.A_BOLD
                            elif t < 7:
                                attr = curses.color_pair(base)
                            else:
                                attr = curses.color_pair(5) | curses.A_DIM

                            stdscr.addstr(yy, x, ch, attr)
                        except curses.error:
                            pass

                layer["cols"][x] += layer["speeds"][x] * (0.8 + intensity * 0.28)
                if abs(layer["cols"][x]) - trail_len >= sh:
                    layer["cols"][x] = random.randint(-40, -1)
                    layer["speeds"][x] = random.uniform(0.55, 2.8) * (1.0 + depth * 0.36)

        if intensity > 2.0 and random.random() < 0.25 * intensity:
            for _ in range(int(3 * intensity)):
                sparks.append({
                    "x": random.randint(0, sw - 1),
                    "y": random.randint(0, sh - 1),
                    "vx": random.choice([-2, -1, 1, 2]),
                    "vy": random.uniform(-1.2, 0.6),
                    "life": random.randint(6, 18)
                })

        new_sparks = []
        for s in sparks:
            s["x"] += s["vx"]
            s["y"] += s["vy"]
            s["life"] -= 1
            if s["life"] > 0 and 0 <= int(s["y"]) < sh and 0 <= int(s["x"]) < sw:
                try:
                    attr = curses.color_pair(random.choice([3, 4, 8])) | curses.A_BOLD
                    stdscr.addstr(int(s["y"]), int(s["x"]), random.choice("·•+*█"), attr)
                except curses.error:
                    pass
                new_sparks.append(s)
        sparks = new_sparks

        if glitch_timer > 0:
            glitch_timer -= 1
        elif random.random() < 0.022 + intensity * 0.012:
            glitch_timer = random.randint(3, 12)

        if glitch_timer > 0:
            if random.random() < 0.65:
                row = random.randint(0, sh - 1)
                shift = random.randint(-14, 14)
                for x in range(sw):
                    try:
                        ch = random.choice(chars) if random.random() < 0.55 else " "
                        pair = random.choice([3, 4, 7, 8])
                        stdscr.addstr(row, x, ch, curses.color_pair(pair) | curses.A_BOLD)
                    except curses.error:
                        pass

            if random.random() < 0.55:
                for _ in range(random.randint(2, 6)):
                    cx = random.randint(0, sw - 1)
                    for yy in range(sh):
                        if random.random() < 0.65:
                            try:
                                stdscr.addstr(yy, cx, random.choice(chars),
                                              curses.color_pair(random.choice([3, 4, 7])) | curses.A_BOLD)
                            except curses.error:
                                pass

            if random.random() < 0.18:
                for _ in range(random.randint(80, 220)):
                    yy = random.randint(0, sh - 1)
                    xx = random.randint(0, sw - 1)
                    try:
                        stdscr.addstr(yy, xx, random.choice(chars),
                                      curses.color_pair(random.choice([3, 4, 7, 8])) | curses.A_BOLD)
                    except curses.error:
                        pass

        logo_h = len(logo)
        logo_w = len(logo[0])
        start_y = max(0, (sh - logo_h) // 2 + y_offset)
        start_x = max(0, (sw - logo_w) // 2)

        if intensity > 3.8:
            pulse = curses.color_pair(3) | curses.A_BOLD
        elif intensity > 2.2:
            pulse = curses.color_pair(8) | curses.A_BOLD
        elif frame % 55 < 9:
            pulse = curses.color_pair(3) | curses.A_BOLD
        elif frame % 55 < 20:
            pulse = curses.color_pair(4) | curses.A_BOLD
        elif frame % 55 < 32:
            pulse = curses.color_pair(7) | curses.A_BOLD
        else:
            pulse = curses.color_pair(2) | curses.A_BOLD

        if glitch_timer > 0 and random.random() < 0.4:
            for i, line in enumerate(logo):
                try:
                    glitched = "".join(random.choice(chars) if random.random() < 0.25 else c for c in line)
                    stdscr.addstr(start_y + i, start_x, glitched, curses.color_pair(3) | curses.A_BOLD)
                except curses.error:
                    pass
        else:
            for i, line in enumerate(logo):
                try:
                    stdscr.addstr(start_y + i, start_x, line, pulse)
                except curses.error:
                    pass

        stdscr.refresh()
        frame += 1
        time.sleep(0.024)

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
