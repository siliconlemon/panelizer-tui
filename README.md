<p style="text-align:left">
  <img src="assets/icon.svg" width="180" alt="panelizer-cli logo" />
</p>

# Panelizer TUI

A TUI (terminal user interface) tool for laying out pictures onto clean, instagram-ready carousel panels. 

<!--suppress CheckImageSize -->
<img width="688" alt="launch-screen" src="/assets/launch-screen.png" />

## Features

- A fast and lightweight `textual-based` TUI.
- Works with all common aspect ratios like 3:4, 4:5, 3:2, and anything between 16:9 and 5:2.
- Fits each picture onto one or two portrait-mode panels (4:5 or 3:4), based on proportional padding for both the horizontal and vertical axis.
- In Constant Border mode, the panels are padded with a constant border, defined by a percentage of the image's width.

## Pricing

This project is open-source and free, forever.

## Contributions

Open to issues and pull requests. If you’ve got a cool idea, improvement suggestion, or a weird edge case, let me know.

## Running in dev mode

The `panelizer.app` module's UI unfortunately does not work in Pycharm's integrated terminal, this might be an issue
with other IDEs as well. Run the module in WT or another dedicated external terminal with support from `textual`
for this to work properly.

- **Install dependencies:** In your project's root directory, run `pip install .` to install all required packages.
- **Run as a module:** Open a new, external terminal and execute `python -m panelizer.app`.
      
## License

MIT License ([@siliconlemon](https://github.com/siliconlemon)) — see [LICENSE](LICENSE) for full text.
