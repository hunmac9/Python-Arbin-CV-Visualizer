# genColors.py
from colour import Color

def generate_gradient_colors(start_color, end_color, num_colors):
    start = Color(start_color)
    end = Color(end_color)
    return [color.hex for color in start.range_to(end, num_colors)]

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate gradient colors and corresponding hex codes.")
    parser.add_argument("start_color", type=str, help="Start color of the gradient (e.g., #440154, #0d0887)")
    parser.add_argument("end_color", type=str, help="End color of the gradient (e.g., #fde725, #fccf25)")
    parser.add_argument("num_colors", type=int, help="Number of colors to generate")
    
    args = parser.parse_args()
    
    colors = generate_gradient_colors(args.start_color, args.end_color, args.num_colors)
    for color in colors:
        print(color)
