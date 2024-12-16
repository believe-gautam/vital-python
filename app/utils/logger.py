class Logger:
    enabled = True  # Central control for all logging

    @staticmethod
    def info(message):
        if Logger.enabled:
            print(f"[INFO] {message}")

    @staticmethod
    def error(message):
        if Logger.enabled:
            print(f"[ERROR] {message}")

    @staticmethod
    def warning(message):
        if Logger.enabled:
            print(f"[WARNING] {message}")

    @staticmethod
    def debug(message):
        if Logger.enabled:
            print(f"[DEBUG] {message}")