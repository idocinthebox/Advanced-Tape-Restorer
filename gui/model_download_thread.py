from PySide6.QtCore import QThread, Signal
import time

from core.ai_model_manager import download_model


class ModelDownloadThread(QThread):
    """QThread to download AI models with progress signals.

    Signals:
        progress(model:str, downloaded:int, total:int)
        model_started(model:str)
        finished_signal(success:bool, message:str)
        error(message:str)
    """

    progress = Signal(str, int, int)
    model_started = Signal(str)
    finished_signal = Signal(bool, str)
    error = Signal(str)

    def __init__(self, models: list[str], parent=None):
        super().__init__(parent)
        self.models = list(models)
        self._cancel = {"cancelled": False}

    def run(self):
        try:
            for m in self.models:
                if self._cancel.get("cancelled"):
                    self.finished_signal.emit(False, "Cancelled")
                    return

                # Retry logic
                max_attempts = 3
                backoff = 1
                attempt = 0
                while attempt < max_attempts:
                    attempt += 1
                    if self._cancel.get("cancelled"):
                        self.finished_signal.emit(False, "Cancelled")
                        return

                    self.model_started.emit(m)

                    def _cb(downloaded, total):
                        # emit progress updates
                        try:
                            self.progress.emit(m, int(downloaded), int(total))
                        except Exception:
                            pass

                    try:
                        download_model(
                            m,
                            accept_license=True,
                            progress_callback=_cb,
                            cancel_flag=self._cancel,
                        )
                        # success
                        break
                    except Exception as e:
                        if self._cancel.get("cancelled"):
                            self.finished_signal.emit(False, "Cancelled")
                            return
                        if attempt < max_attempts:
                            # emit retry notification and backoff
                            self.error.emit(
                                f"Download {m} failed (attempt {attempt}/{max_attempts}): {e}. Retrying in {backoff}s..."
                            )
                            time.sleep(backoff)
                            backoff *= 2
                            continue
                        else:
                            # final failure
                            self.error.emit(
                                f"Download {m} failed after {max_attempts} attempts: {e}"
                            )
                            self.finished_signal.emit(False, str(e))
                            return

            self.finished_signal.emit(True, "All models downloaded")
        except Exception as e:
            if self._cancel.get("cancelled"):
                self.finished_signal.emit(False, "Cancelled")
            else:
                self.error.emit(str(e))
                self.finished_signal.emit(False, str(e))

    def request_cancel(self):
        self._cancel["cancelled"] = True
