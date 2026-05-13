NUMBERS = list(range(1, 50))  # 1-49
TOTAL_NUMBERS = 49

# Color scheme for number balls (HKJC style)
# Red balls: numbers 1-49 are divided into 3 colors
RED_NUMBERS = {1, 2, 7, 8, 12, 13, 18, 19, 23, 24, 29, 30, 34, 35, 40, 45, 46}
BLUE_NUMBERS = {3, 4, 9, 10, 14, 15, 20, 25, 26, 31, 36, 37, 41, 42, 47, 48}
GREEN_NUMBERS = {5, 6, 11, 16, 17, 21, 22, 27, 28, 32, 33, 38, 39, 43, 44, 49}


def get_ball_color(num: int) -> str:
    if num in RED_NUMBERS:
        return "red"
    elif num in BLUE_NUMBERS:
        return "blue"
    return "green"
