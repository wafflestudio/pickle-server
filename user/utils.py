import io
from PIL import Image, ImageDraw
import cv2
import numpy as np
import easyocr

reader = easyocr.Reader(["en"])


def hough_lines(image: Image, filter: bool = True):
    img = np.array(image)
    height, width, _ = img.shape

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    edges = cv2.Canny(gray, 30, 40, apertureSize=5)

    kernel = np.ones((3, 3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)

    kernel = np.ones((5, 5), np.uint8)
    edges = cv2.erode(edges, kernel, iterations=1)

    lines = cv2.HoughLines(edges, 1, np.pi / 180, 150)

    if not lines.any():
        print("No lines were found")
        exit()

    if filter:
        rho_threshold = 15
        theta_threshold = 0.1

        # how many lines are similar to a given one
        similar_lines = {i: [] for i in range(len(lines))}
        for i in range(len(lines)):
            for j in range(len(lines)):
                if i == j:
                    continue

                rho_i, theta_i = lines[i][0]
                rho_j, theta_j = lines[j][0]
                if (
                    abs(rho_i - rho_j) < rho_threshold
                    and abs(theta_i - theta_j) < theta_threshold
                ):
                    similar_lines[i].append(j)

        # ordering the INDECES of the lines by how many are similar to them
        indices = [i for i in range(len(lines))]
        indices.sort(key=lambda x: len(similar_lines[x]))

        # line flags is the base for the filtering
        line_flags = len(lines) * [True]
        for i in range(len(lines) - 1):
            if not line_flags[
                indices[i]
            ]:  # if we already disregarded the ith element in the ordered list then we don't care (we will not delete anything based on it and we will never reconsider using this line again)
                continue

            for j in range(
                i + 1, len(lines)
            ):  # we are only considering those elements that had less similar line
                if not line_flags[
                    indices[j]
                ]:  # and only if we have not disregarded them already
                    continue

                rho_i, theta_i = lines[indices[i]][0]
                rho_j, theta_j = lines[indices[j]][0]
                if (
                    abs(rho_i - rho_j) < rho_threshold
                    and abs(theta_i - theta_j) < theta_threshold
                ):
                    line_flags[indices[j]] = (
                        False  # if it is similar and have not been disregarded yet then drop it now
                    )

    filtered_lines = []

    if filter:
        for i in range(len(lines)):  # filtering
            if line_flags[i]:
                filtered_lines.append(lines[i])

    else:
        filtered_lines = lines

    x_lines = []
    y_lines = []
    for line in filtered_lines:
        rho, theta = line[0]
        a = np.cos(theta)
        b = np.sin(theta)
        x1 = int(a * rho)
        y1 = int(b * rho)

        if (theta > 0.01 and theta < 3.13) and (theta < 1.56 or theta > 1.58):
            continue

        if theta == 0.00:
            x2 = x1
            y2 = y1 + height
            color = (255, 0, 0)
        else:
            x2 = int(x1 + width * b)
            y2 = int(y1 - height * a)
            color = (0, 0, 255)

        if x1 == x2:
            x_lines.append(x1)
        else:
            y_lines.append(y1)

    return sorted(x_lines), sorted(y_lines)


def run(image_bytes):
    from PIL import Image, ImageFilter
    from PIL import Image, ImageOps

    def invert_to_white_background(image):
        # Convert to grayscale to simplify the check
        gray = image.convert("L")

        # Calculate the mean, assuming darker image if mean is less than 128
        is_dark = sum(gray.getdata()) / len(gray.getdata()) < 128

        # Invert image if it's dark
        if is_dark:
            inverted_image = ImageOps.invert(image)
        else:
            inverted_image = image

        return inverted_image

    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image = invert_to_white_background(image)

    # cut 0~7% of the left side
    width, height = image.size
    l_007_cropped_image = image.crop((0, 0, int(width * 0.07), height))
    l_007_cropped_image = invert_to_white_background(l_007_cropped_image)
    l_007_cropped_image = l_007_cropped_image.filter(ImageFilter.MinFilter(size=3))

    from local_scripts.cv2 import hough_lines

    l_080_cropped_image = image.crop((0, 0, int(width * 0.80), height))
    l_080_cropped_image = invert_to_white_background(l_080_cropped_image)
    _, grid_y_lines = hough_lines(l_080_cropped_image)
    grid_y_lines = sorted(set(grid_y_lines))

    t_cropped_image = image.crop((0, 0, width, int(height * 0.15)))
    t_cropped_image = invert_to_white_background(t_cropped_image)
    grid_x_lines, _ = hough_lines(t_cropped_image)
    grid_x_lines = sorted(set(grid_x_lines))

    # read timetable hour (int) from cropped image
    import numpy as np

    allowlist = "1234567890"

    image_np = np.array(l_007_cropped_image)
    result = reader.readtext(
        image_np,
        allowlist=allowlist,
    )

    def get_ypos_hour_list(result):
        """
        get y position and hour from result
        output: [
            {
            "ypos": int,
            "hour": int
            }
        ]
        """
        ypos_hour_list = []
        for i, detection in enumerate(result):
            bbox = detection[0]
            ypos = bbox[0][1]
            hour = int(detection[1])
            ypos_hour_list.append({"index": i, "ypos": ypos, "hour": hour})
        return ypos_hour_list

    # find most nearest, less y_line among y_lines, with ypos

    def fill_y_lines(y_lines, ypos_hour_list):
        def find_nearest_y_line(ylines, ypos):
            """
            find nearest y line from ypos
            """
            lower_y_lines = [y for y in ylines if y < ypos]
            nearest_y_line = max(lower_y_lines)

            return nearest_y_line

        for ypos_hour in ypos_hour_list:
            nearest_y_line = find_nearest_y_line(y_lines, ypos_hour["ypos"])
            ypos_hour["y_line"] = nearest_y_line

        # check same y_line, if same, keep only nearest one
        from collections import defaultdict

        y_line__ypos_hour_list = defaultdict(list)
        for ypos_hour in ypos_hour_list:
            y_line__ypos_hour_list[ypos_hour["y_line"]].append(ypos_hour)

        for y_line, same_ypos_hour_list in y_line__ypos_hour_list.items():
            if len(same_ypos_hour_list) > 1:
                # keep only nearest one
                nearest_ypos_hour = min(
                    same_ypos_hour_list,
                    key=lambda ypos_hour: abs(ypos_hour["ypos"] - y_line),
                )

                for ypos_hour in same_ypos_hour_list:
                    if ypos_hour != nearest_ypos_hour:
                        ypos_hour["y_line"] = None

        return ypos_hour_list

    ypos_hour_list = get_ypos_hour_list(result)
    ypos_hour_list = fill_y_lines(grid_y_lines, ypos_hour_list)

    y_lines = [i["y_line"] for i in ypos_hour_list]
    # draw x line, nearest y line as grid
    draw = ImageDraw.Draw(image)

    for x in grid_x_lines:
        draw.line([x, 0, x, height], fill="black", width=2)

    def get_distance_dict_list(lines: list[int]) -> list[dict]:
        # print distance between each item of y_lines
        distance_dict_list = []

        for i in range(len(lines)):
            current_item = lines[i]
            if current_item is None:
                distance_dict_list.append(
                    {
                        "index": i,
                        "y_line": None,
                        "before_distance": None,
                        "after_distance": None,
                    }
                )
                continue
            if i == 0:
                before_item = None
                after_item = lines[i + 1]
            elif i == len(lines) - 1:
                before_item = lines[i - 1]
                after_item = None
            else:
                before_item = lines[i - 1]
                after_item = lines[i + 1]

            before_distance = None
            after_distance = None
            if before_item:
                before_distance = current_item - before_item
            if after_item:
                after_distance = after_item - current_item

            if before_distance is None and after_distance is None:
                continue

            if before_distance is None:
                before_distance = after_distance
            elif after_distance is None:
                after_distance = before_distance

            distance_dict_list.append(
                {
                    "index": i,
                    "y_line": lines[i],
                    "before_distance": before_distance,
                    "after_distance": after_distance,
                }
            )
        return distance_dict_list

    def get_unit_distance(distance_dict_list):
        unit_distance = sum(
            [
                i["before_distance"] + i["after_distance"]
                for i in distance_dict_list
                if i["before_distance"] and i["after_distance"]
            ]
        ) / (len(distance_dict_list) * 2)
        unit_distance = int(unit_distance)
        return unit_distance

    distance_dict_list = get_distance_dict_list(y_lines)
    unit_distance = get_unit_distance(distance_dict_list)

    # drop items with distance difference more than 10% of unit_distance
    def accept_distance(distance_dict, unit_distance):
        if (
            distance_dict["before_distance"] is None
            or distance_dict["after_distance"] is None
        ):
            return False
        bound = 0.2 * unit_distance
        return (
            abs(distance_dict["before_distance"] - unit_distance) < bound
            and abs(distance_dict["after_distance"] - unit_distance) < bound
        )

    filtered_y_lines = [
        i["y_line"] if accept_distance(i, unit_distance) else None
        for i in distance_dict_list
    ]

    def fix_linear_distribution_with_none(data):
        import numpy as np
        from scipy.stats import linregress

        # Filter out None values and perform linear regression on the remaining data
        available_data = [(i, x) for i, x in enumerate(data) if x is not None]
        indices, values = zip(*available_data)
        slope, intercept, _, _, _ = linregress(indices, values)

        # Generate a new list with equal spacing, replacing None values
        new_list = [
            slope * i + intercept if data[i] is None else data[i]
            for i in range(len(data))
        ]

        return [int(round(x)) for x in new_list]

    # Example usage with the provided list
    original_list = [161, 245, 413, 497, 581, 639, 748, 832, 916, 990, 1083]
    fixed_list = fix_linear_distribution_with_none(original_list)
    fixed_list

    filtered_y_lines = fix_linear_distribution_with_none(filtered_y_lines)
    for y in filtered_y_lines:
        draw.line([0, y, width, y], fill="black", width=2)

    # fill ypos_hour_list with filtered_y_lines
    for ypos_hour, y_line in zip(ypos_hour_list, filtered_y_lines):
        ypos_hour["y_line"] = y_line

    from dataclasses import dataclass

    @dataclass
    class TimeTableQuarter:
        weekday: int  # 0: mon, 1: tue, 2: wed, 3: thu, 4: fri  # 5: sat
        hour: int
        quarter: int  # 0: 0~25%, 1: 25~50%, 2: 50~75%, 3: 75~100%
        is_filled: bool
        #
        left: int
        top: int
        right: int
        bottom: int

    grid_x_distance_dict_list = get_distance_dict_list(grid_x_lines)
    grid_x_unit_distance = get_unit_distance(grid_x_distance_dict_list)

    appended_grid_x_lines = grid_x_lines
    maybe_append_last_x_line = grid_x_lines[-1] + grid_x_unit_distance
    if maybe_append_last_x_line < width + 20:
        appended_grid_x_lines.append(maybe_append_last_x_line)

    grid_y_distance_dict_list = get_distance_dict_list(filtered_y_lines)
    grid_y_unit_distance = get_unit_distance(grid_y_distance_dict_list)
    append_grid_y_lines = filtered_y_lines
    maybe_append_last_y_line = filtered_y_lines[-1] + grid_y_unit_distance
    if maybe_append_last_y_line < height + 20:
        append_grid_y_lines.append(maybe_append_last_y_line)

    def quarter_boxs_filled_ratio(img, bbox):

        l, t, r, b = bbox
        img = img.crop((l, t, r, b))
        img_data = np.array(img)

        quarter_height = img_data.shape[0] // 4  # Use height instead of width
        filled_status = []

        for i in range(4):
            quarter = img_data[i * quarter_height : (i + 1) * quarter_height, :]

            # get inside of quarter (10% of all side)
            quarter = quarter[
                int(quarter_height * 0.20) : int(quarter_height * 0.80),
                int((r - l) * 0.20) : int((r - l) * 0.80),
            ]

            def is_whity(rgb):
                diffs = [abs(rgb[i] - rgb[(i + 1) % 3]) for i in range(3)]
                max_dif = max(diffs)
                return max_dif < 32

            filled = not is_whity(np.mean(quarter, axis=(0, 1)))
            filled_status.append(filled)

        return filled_status

    time_table_boxes = []
    for y_idx in range(len(append_grid_y_lines) - 1):  # hour
        for x_idx in range(len(appended_grid_x_lines)):  # weekday
            if x_idx == 0:
                continue
            weekday = x_idx - 1
            hour = ypos_hour_list[y_idx]["hour"]
            left = appended_grid_x_lines[x_idx - 1]
            right = appended_grid_x_lines[x_idx]
            top = append_grid_y_lines[y_idx]
            bottom = append_grid_y_lines[y_idx + 1]

            bbox = (left, top, right, bottom)
            quarters_filled = quarter_boxs_filled_ratio(image, bbox)

            for i, quarter_filled in enumerate(quarters_filled):
                tt_quarter = TimeTableQuarter(
                    weekday=weekday,
                    hour=hour,
                    quarter=i,
                    is_filled=quarter_filled,
                    left=left,
                    top=top + i * (bottom - top) / 4,
                    right=right,
                    bottom=top + (i + 1) * (bottom - top) / 4,
                )

                time_table_boxes.append(tt_quarter)

    def find_free_time_slots(timetable):
        free_slots = []

        # Group the timetable by weekdays
        timetable_by_day = [[] for _ in range(6)]
        for slot in timetable:
            timetable_by_day[slot.weekday].append(slot)

        # For each day, sort the slots by hour and then by quarter
        for day_slots in timetable_by_day:
            day_slots.sort(key=lambda slot: (slot.hour, slot.quarter))

            # Iterate over slots and find free periods
            i = 0
            while i < len(day_slots):
                if not day_slots[i].is_filled:
                    start = i
                    # Find the end of the continuous free period
                    while i < len(day_slots) and not day_slots[i].is_filled:
                        i += 1
                    end = i - 1

                    # Check if the free period is surrounded by lectures
                    if (
                        start > 0
                        and end < len(day_slots) - 1
                        and day_slots[start - 1].is_filled
                        and day_slots[end + 1].is_filled
                    ):
                        free_slots.extend(day_slots[start : end + 1])
                else:
                    i += 1

        return free_slots

    free_slots = find_free_time_slots(time_table_boxes)

    opacity = 0.8
    overlay = Image.new("RGB", image.size, "white")
    black_image = image.copy().convert("RGB").convert("L").convert("RGB")
    output_image = Image.blend(black_image, overlay, opacity)
    coloring = "#7ab5d6"
    for slot in free_slots:
        draw = ImageDraw.Draw(output_image)
        draw.rectangle(
            [slot.left, slot.top, slot.right, slot.bottom],
            fill=coloring,
        )

    return output_image
