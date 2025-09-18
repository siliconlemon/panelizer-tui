
def paint(*, ascii_string: str, color_map: dict) -> str:
    """
    Applies color tags to continuous runs of characters in an ASCII art string.

    Args:
        ascii_string: The raw ASCII art string from a text file.
        color_map: A dictionary mapping characters to color names or hex codes.

    Returns:
        The colorized string with Textual color tags.
    """
    output_lines = []
    for line in ascii_string.splitlines():
        if not line:
            output_lines.append("")
            continue

        colorized_line = ""
        current_char = line[0]
        current_color = color_map.get(current_char)
        start_index = 0

        for i in range(1, len(line)):
            next_char = line[i]
            if next_char != current_char or color_map.get(next_char) != current_color:
                substring = line[start_index:i]
                if current_color:
                    colorized_line += f"[{current_color}]{substring}[/{current_color}]"
                else:
                    colorized_line += substring
                current_char = next_char
                current_color = color_map.get(current_char)
                start_index = i

        final_substring = line[start_index:]
        if current_color:
            colorized_line += f"[{current_color}]{final_substring}[/{current_color}]"
        else:
            colorized_line += final_substring
        output_lines.append(colorized_line)

    return "\n".join(output_lines)