<p style="text-align:left">
  <img src="assets/icon.svg" width="180" alt="panelizer-cli logo" />
</p>

# panelizer-cli

A CLI tool for laying out portrait or landscape images into clean, instagram-ready carousel panels.

## Features

- Fast and lightweight CLI
- Automatically identifies images in 3:4, 4:5, 3:2, and anything between 16:9 and 5:2
- Puts images into one or more 2000×2500px (instagram-ready) portrait panels, based on image width thresholds like 16:9

## Pricing

This project is open-source and free, forever.

## Contributions

Open to issues and pull requests. If you’ve got a cool idea, improvement suggestion, or a weird edge case, let me know.

## Running in dev mode

The `panelizer.app` module's UI unfortunately does not work in Pycharm's integrated terminal, this might be an issue
with other IDEs as well. Run the module in WT or another dedicated external terminal with support from textual
for this to work properly.

- **Install dependencies:** In your project's root directory, run `pip install .` to install all required packages.
- **Run as a module:** Open a new, external terminal and execute `python -m panelizer.app`.

Reminder:

- **Check Path**: Don't be a dummy and make sure that your interpreter is added to Windows' system *Path* variable. 

    Otherwise, you'll get something like this: `$ python -m panelizer/app Python was not found; run without arguments to install from the Microsoft Store, 
      or disable this shortcut from...`
      

## License

MIT License ([@siliconlemon](https://github.com/siliconlemon)) — see the [LICENSE](LICENSE) file for full text.
