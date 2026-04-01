import json
import os
import heapq

class Event:
    def __init__(self, data: dict):
        self._datetime = data.get("datetime")
        self._event_type = data.get("event_type")
        self._message_template = data.get("message", "")
        self._params = data.get("params", {})

        try:
            self._message = self._message_template.format(**self._params)
        except(KeyError, IndexError):
            self._message = self._message_template

    def __repr__(self):
        return f"<{self._event_type} {self._datetime}: {self._message}>"

class LogManager:
    def __init__(self, path: str):
        self._path = path
        self._error_cache = {}

    def _lines_iter(self, path):
        with open(path, "rb") as file:
            file.seek(0, 2)
            cursor = file.tell()
            buffer = b""
            buffer_size = 1024

            while cursor > 0:
                step = min(cursor, buffer_size)
                cursor -= step
                file.seek(cursor)
                chunk = file.read(step)
                buffer = chunk + buffer

                lines = buffer.split(b"\n")
                buffer = lines.pop(0)

                for line in reversed(lines):
                    if line:
                        yield Event(json.loads(line.decode('utf-8').strip()))
            
            if buffer.strip():
                yield Event(json.loads(buffer.decode('utf-8').strip()))

    def get_last_N_logs_for_service(self, service_name: str, n: int) -> list:
        files = sorted([f for f in os.listdir(self._path) if f.startswith(f"{service_name}_")])[::-1]

        find_logs = 0
        logs = []

        for file in files:
            full_path = os.path.join(self._path, file)

            for event in self._lines_iter(full_path):
                logs.append(event)
                find_logs += 1

                if find_logs >= n:
                    return logs
                
        return logs
    
    def get_last_N_logs_all_service(self, n: int) -> list:
        files = sorted([f for f in os.listdir(self._path)])[::-1]

        streams = [self._lines_iter(os.path.join(self._path, f)) for f in files]

        merged_stream = heapq.merge(*streams, key=lambda x: x._datetime, reverse=True)

        logs = []
        for event in merged_stream:
            logs.append(event)
            if len(logs) >= n:
                return logs
            
        return logs
    
    def get_last_N_logs_with_param(self, param, n):
        files = sorted([f for f in os.listdir(self._path)])[::-1]

        streams = [self._lines_iter(os.path.join(self._path, f)) for f in files]

        merged_stream = heapq.merge(*streams, key=lambda x: x._datetime, reverse=True)

        logs = []
        for event in merged_stream:
            if param in event._params.values():
                logs.append(event)

            if len(logs) >= n:
                return logs
            
        return logs
    
    def get_error_count_by_service(self, start: str, end: str) -> dict:
        files = os.listdir(self._path)
        service_errors = {}

        for file in files:
            service_name, date = file.replace(".log", "").split("_")

            if start <= date <= end:
                if file not in self._error_cache:
                    count = 0
                    for event in self._lines_iter(os.path.join(self._path, file)):
                        if event._event_type == "ERROR":
                            count += 1
                    self._error_cache[file] = count

                error_count = self._error_cache[file]
                service_errors[service_name] = service_errors.get(service_name, 0) + error_count

        return service_errors
    
    def get_dates_last_error(self) -> dict:
        files = sorted([f for f in os.listdir(self._path)])[::-1]

        last_error = {}

        for file in files:
            service_name, _ = file.replace(".log", "").split("_")

            if service_name in last_error:
                continue

            full_path = os.path.join(self._path, file)

            for event in self._lines_iter(full_path):
                if event._event_type == "ERROR":
                    last_error[service_name] = event._datetime
                    break
        return last_error
