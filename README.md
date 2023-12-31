# Zefoy-TikTok-Bot

![GitHub License](https://img.shields.io/badge/license-MIT-blue.svg)

Zefoy-TikTok-Bot is an open-source Python utility that enables you to boost your tiktok engagement such as views, likes, followers, comments, favorites, and shares through a reverse engineered website (zefoy.com)

## Table of Contents
- [Background](#background)
- [Features](#features)
- [Goals](#goals)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Background
This project was originally created because I wanted to learn how zefoy.com worked and I was intrigued by their efforts at blocking any sort of dev tools access. They essentially created an infinite amount of breakpoints which when you would open dev tools, your entire browser would crash from the amount of breakpoints it was activating. I bypassed this by opening the site in chrome and modifying the javascript to simply delete the line of code that created all of those pesky breakpoints.

## Features

- Fully requests based and uses BeautifulSoup4
- Bypasses/solves captcha without need for 3rd party service
- Proxy support
- Reverse engineered website for their API
- Uses real data to fake connections to website to allow for anonymity and bypass detection
- Loop Support

### Goals
- [ ] Make GUI look better
- [ ] Optmize and refactor code (was created in less than a day)
- [ ] Add ability to interact with unsupported features

## Getting Started
Before using Zefoy-TikTok-Bot, make sure you have the following dependencies installed:

- Python 3.8+
- `pip install -r requirements.txt`
  
- Within the python script ensure you enter the path of your tesseract ocr installation
- Add proxy if desired in format accepted by python requests

## Usage
Follow whatever the GUI prompts
Ensure tiktok URL is accurate before usage

## Contributing

Contributions are welcome. You can contribute by reporting issues, suggesting improvements, or submitting pull requests. To get started:

    Fork this repository.
    Create a new branch for your feature or bug fix: git checkout -b feature/your-feature.
    Make your changes and commit them.
    Push to your fork: git push origin feature/your-feature.
    Create a pull request.

Please ensure your code adheres to proper coding standards and includes relevant tests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

If you have any questions or need assistance, feel free to reach out.
