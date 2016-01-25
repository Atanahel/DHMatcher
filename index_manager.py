
import threading
from replica.indexes import indexes
import time


class IndexManager:

    def _thread(self):
        while True:
            time.sleep(self.period)

            with self._lock:
                if self.need_rebuilding:
                    print("Index rebuilding...")
                    rebuilding_task = indexes.create_index.delay(self.feature_name)
                    self.need_rebuilding = False
                else:
                    rebuilding_task = None

            if rebuilding_task is not None:
                rebuilding_task.wait()
                if rebuilding_task.successful():
                    print("Index rebuilt, reload it...")
                    new_index = indexes.load_index(self.feature_name)
                    with self._lock:
                        self._current_index = new_index
                else:
                    print("Index rebuilding failed...")

    def __init__(self, feature_name=indexes.CNN_FEATURE_NAMES[0], period=15):
        """

        :param period: Time in minutes of the rebuilding process
        :return:
        """
        self.period = period*60
        self.feature_name = feature_name
        self._lock = threading.Lock()
        try:
            self._current_index = indexes.load_index(feature_name)  # type: indexes.RawIndex
        except FileNotFoundError:
            self._current_index = None
        self.need_rebuilding = False

        threading.Thread(target=self._thread, daemon=True).start()

    def search(self, *args, **kwargs):
        if self._current_index is None:
            return []
        with self._lock:
            return self._current_index.search(*args, **kwargs)

    def ask_for_index_rebuilding(self):
        with self._lock:
            self.need_rebuilding = True
