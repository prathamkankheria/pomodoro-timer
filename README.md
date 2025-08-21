# Pomodoro Timer with History

A modern, minimalist Pomodoro Timer built with Tkinter that tracks your daily work and break sessions, persists history to a file, and lets you view the full history in a popup window. This application can be bundled as a standalone executable with PyInstaller.

## Features

- Work / Short Break / Long Break modes  
- Real-time tracking of work and break durations  
- Daily goal setting and progress display  
- Persistent history stored in `pomodoro_history.txt` alongside the app  
- **View History** button to inspect all past sessions  
- Clean, minimalist UI with customizable fonts  
- Desktop notifications via simple beep sounds  
- Easily packaged into a standalone `.exe` with PyInstaller  

## Installation

1. Clone or download this repository:  
   ```bash
   git clone https://github.com/prathamkankheria/pomodoro-timer.git
   cd pomodoro-timer
   ```

2. (Optional) Create and activate a virtual environment:  
   ```bash
   python -m venv venv
   venv\Scripts\activate    # Windows
   source venv/bin/activate # macOS / Linux
   ```

3. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```  
   _Only `tkinter` and standard-library modules are used; ensure you have a Python installation with `tkinter` support._

## Usage

Run the application with:

```bash
python pomodoro_timer_with_history.py
```

- **Start** begins a session in the selected mode.  
- **Pause** suspends the timer.  
- **Reset** returns to the default work timer (25m).  
- **Mode menu** switches between Work / Short Break / Long Break.  
- **Daily Goal** entry lets you set your target work minutes per day.  
- **View History** opens a window showing all recorded daily stats.  

## Packaging as a Standalone App

Use [PyInstaller](https://www.pyinstaller.org/) to bundle into a single executable:

```bash
pip install pyinstaller
python -m pyinstaller --onefile --windowed pomodoro.py
```

- The standalone executable will appear in the `dist/` directory.  
- The `pomodoro_history.txt` file will be created alongside the executable to store history.

## File Structure

```
pomodoro.py                     # Main application script  
pomodoro_history.txt            # Auto-created history file  
README.md                       # This documentation  
requirements.txt                # (Optional) listed dependencies  
```

## Contributing

Contributions, bug reports, and feature requests are welcome!  
1. Fork the repository.  
2. Create a new branch: `git checkout -b feature/my-feature`.  
3. Commit your changes: `git commit -m "Add my feature"`.  
4. Push to your branch and open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
