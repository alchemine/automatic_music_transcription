# base-project: Basic Project Environment for Python Development

This project aims to build a Python project environment based on various useful tools.

## 1. Development Environment

To provide a consistent development experience across different platforms, I have set up the following environment:

- **Dev Container**: Utilizes Visual Studio Code's Dev Containers to provide a consistent development environment.
  - Configuration file: `.devcontainer/devcontainer.json`
- **Docker**: Supports containerization for deployment and testing.
  - Configuration file: `Dockerfile`
- **Python**:
  - Project configuration: `pyproject.toml`
  - Dependency management: `requirements.txt`

## 2. Core Utilities

The `src/core/` directory includes several utility modules to enhance development productivity.

### 2.1 Timer

Provides functionality to measure code execution time.

1. **Context manager**

   ```python
   from src.core import Timer

   with Timer("Task 1"):
       # Here is code snippet
       sleep(1)
   ```

   Output:

   ```
   * Task 1    | 1.00s (0.02m)
   ```

2. **Decorator**

   ```python
   from src.core import Timer, T

   @Timer("Task 1")
   def fn1():
       sleep(1)

   @T
   def fn2():
       sleep(1)

   fn1()
   fn2()
   ```

   Output:

   ```
   * Task 1     | 1.00s (0.02m)
   * fn2()      | 1.00s (0.02m)
   ```

### 2.2 Depth logging

Provides functionality to visualize the function call stack and measure execution time.

```python
from src.core import D

@D
def main():
    main1()
    main2()

@D
def main1():
    main11()
    main12()

@D
def main11():
    return

@D
def main12():
    return

@D
def main2():
    main21()

@D
def main21():
    return

main()
```

Output:

```
  1            | main()
  1.1          | main1()
  1.1.1        | main11()
* 1.1.1        | 0.00s (0.00m)
  1.1.2        | main12()
* 1.1.2        | 0.00s (0.00m)
* 1.1          | 0.00s (0.00m)
  1.2          | main2()
  1.2.1        | main21()
* 1.2.1        | 0.00s (0.00m)
* 1.2          | 0.00s (0.00m)
* 1            | 0.00s (0.00m)
```

### 2.3 Logging

Records logs to both console and file. \
Logs are saved in the `logs/YYYY-MM-DD.log` file for easy tracking and debugging. \
Utility functions allow for easy use.

```python
from src.core import slog, log_info, log_success, log_error, log_warning, log_api
from src.core.logger import STYLES

log_info("This is an info message.")
log_success("This is a success message.")
log_error("This is an error message.")
log_warning("This is a warning message.")
log_api("This is an API message.")
for style in STYLES:
    slog(f"This is a {style} message.", style=style)
```

![alt text](assets/image.png)

### 2.4 Safe HTTP requests

Allows for safe HTTP requests (`requests.post`) including error handling and logging.

```python
from src.core import safe_post

url = "https://httpbin.org/post"
json = {"key": "value"}
response = safe_post(url, json)
```

---

I hope this project helps improve your Python development experience!
