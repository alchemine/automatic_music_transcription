# base-project: Base project environment

---

# 1. Development environment

- [Dev container](https://code.visualstudio.com/docs/devcontainers/containers)
  - `.devcontainer/devcontainer.json`
- Docker
  - `Dockerfile`
- Python
  - `pyproject.toml`
  - `requirements.txt`

# 2. Utilities

## 2.1 Timer

1. Context manager

   - `Timer(name)`

     ```python
     from src.core import Timer

     with Timer("Code1"):
         sleep(1)
     ```

     ```
     * Code1        | 1.00s (0.02m)
     ```

2. Decorator

   - `@Timer(name)`
   - `@T`

     ```python
     from src.core import Timer, T

     @Timer("fn1")
     def fn1():
         sleep(1)

     @T
     def fn2():
         sleep(1)

     fn1()
     fn2()
     ```

     ```
     * fn1()        | 1.00s (0.02m)
     * fn2()        | 1.00s (0.02m)
     ```

## 2.2 Depth logging

1. Decorator

   - `@D`

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


     if __name__ == "__main__":
         main()
     ```

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

## 2.3 Logging

1. `slog`

   ```python
   from src.core import slog
   from src.core.logger import STYLES

   for style in STYLES:
       slog(f"This is a {style} message.", style=style)
   ```

   ```
   [2024/08/28 02:37:05] INFO    | This is a ENDC message.
   ...
   [2024/08/28 02:37:05] INFO    | This is a OKCYAN message.
   ```

2. `log_info`, `log_success`, `log_error`, `log_warning`, `log_api`

   ```python
   from src.core import log_info

   log_info("This is an info message.")
   log_success("This is a success message.")
   log_error("This is an error message.")
   log_warning("This is a warning message.")
   log_api("This is an API message.")
   ```

   ```
   [2024/08/28 02:37:05] INFO    | This is an info message.
   [2024/08/28 02:37:05] INFO    | This is a success message.
   [2024/08/28 02:37:05] ERROR   | This is an error message.
   [2024/08/28 02:37:05] WARNING | This is a warning message.
   [2024/08/28 02:37:05] INFO    | Request API:
   [2024/08/28 02:37:05] INFO    | This is an API message.
   ```

## 2.4 Safe post

```python
from src.core import safe_post

url = "https://httpbin.org/post"
json = {"key": "value"}
response = safe_post(url, json)
```

```
[2024/08/28 02:43:32] INFO    | Request API:
[2024/08/28 02:43:32] INFO    | {
  "url": "https://httpbin.org/post",
  "headers": {
    "accept": "application/json",
    "Content-Type": "application/json"
  },
  "json": {
    "key": "value"
  },
  "reproduction_code": "import requests; requests.post(url='https://httpbin.org/post', headers={'accept': 'application/json', 'Content-Type': 'application/json'}, json={'key': 'value'})"
}
```
