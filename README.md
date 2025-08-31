<p style="text-align:left">
  <img src="assets/icon.svg" width="180" alt="panelizer-cli logo" />
</p>

# panelizer-cli

A CLI tool for laying out picturess onto clean, instagram-ready carousel panels. 

## Features

- A fast and lightweight `textual-based` CLI 
- Works with all common aspect ratios like 3:4, 4:5, 3:2, and anything between 16:9 and 5:2
- Fits every picture onto one or two 2000×2500px portrait mode panels, based on proportional padding for both the horizontal and vertical axis

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

Reminder:

- **Check Path**: Don't be a dummy and make sure that your interpreter is added to Windows' system *Path* variable. 

    Otherwise, you'll get something like this: `Python was not found; run without arguments to install from the Microsoft Store, 
      or disable this shortcut from...`
      

## License

MIT License ([@siliconlemon](https://github.com/siliconlemon)) — see the [LICENSE](LICENSE) file for full text.
