"""
Threaded I/O Manager
Parallel disk operations to eliminate I/O bottlenecks during video processing

Features:
- Async file reading/writing with thread pools
- Buffered streaming for large files
- Progress tracking for long operations
- Automatic resource cleanup
- Thread-safe queue-based operations
"""

import os
import queue
import shutil
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional, Callable, List, Tuple, Any, BinaryIO
import hashlib


# Constants
DEFAULT_BUFFER_SIZE = 8 * 1024 * 1024  # 8MB chunks
DEFAULT_MAX_WORKERS = 4  # Maximum parallel I/O threads
QUEUE_TIMEOUT = 0.1  # Seconds to wait for queue operations


class AsyncFileReader:
    """
    Asynchronous file reader with buffered streaming.
    
    Reads file in background thread while main thread processes data.
    Eliminates wait time between read operations.
    """
    
    def __init__(
        self,
        file_path: str,
        buffer_size: int = DEFAULT_BUFFER_SIZE,
        queue_size: int = 4
    ):
        """
        Initialize async file reader.
        
        Args:
            file_path: Path to file to read
            buffer_size: Size of each read chunk
            queue_size: Number of chunks to buffer ahead
        """
        self.file_path = file_path
        self.buffer_size = buffer_size
        self.queue_size = queue_size
        
        self.data_queue = queue.Queue(maxsize=queue_size)
        self.stop_event = threading.Event()
        self.error = None
        self.reader_thread = None
        self.bytes_read = 0
        self.total_size = os.path.getsize(file_path)
    
    def start(self):
        """Start background reading thread."""
        self.reader_thread = threading.Thread(target=self._read_loop, daemon=True)
        self.reader_thread.start()
    
    def _read_loop(self):
        """Background thread that reads file and queues chunks."""
        try:
            with open(self.file_path, 'rb') as f:
                while not self.stop_event.is_set():
                    chunk = f.read(self.buffer_size)
                    if not chunk:
                        # End of file
                        self.data_queue.put(None)  # Sentinel
                        break
                    
                    # Block if queue is full (backpressure)
                    while not self.stop_event.is_set():
                        try:
                            self.data_queue.put(chunk, timeout=QUEUE_TIMEOUT)
                            self.bytes_read += len(chunk)
                            break
                        except queue.Full:
                            continue
        
        except Exception as e:
            self.error = e
            self.data_queue.put(None)  # Signal error
    
    def read(self, timeout: Optional[float] = None) -> Optional[bytes]:
        """
        Read next chunk from queue.
        
        Args:
            timeout: Max seconds to wait for data
        
        Returns:
            Bytes chunk or None if EOF/error
        """
        try:
            chunk = self.data_queue.get(timeout=timeout)
            if chunk is None and self.error:
                raise self.error
            return chunk
        except queue.Empty:
            return None
    
    def stop(self):
        """Stop reading thread."""
        self.stop_event.set()
        if self.reader_thread:
            self.reader_thread.join(timeout=2.0)
    
    def get_progress(self) -> float:
        """Get read progress percentage."""
        if self.total_size == 0:
            return 0.0
        return (self.bytes_read / self.total_size) * 100.0
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


class AsyncFileWriter:
    """
    Asynchronous file writer with buffered output.
    
    Writes data in background thread to prevent blocking main thread.
    """
    
    def __init__(
        self,
        file_path: str,
        buffer_size: int = DEFAULT_BUFFER_SIZE,
        queue_size: int = 8
    ):
        """
        Initialize async file writer.
        
        Args:
            file_path: Path to output file
            buffer_size: Size to buffer before writing
            queue_size: Number of chunks to queue
        """
        self.file_path = file_path
        self.buffer_size = buffer_size
        self.queue_size = queue_size
        
        self.data_queue = queue.Queue(maxsize=queue_size)
        self.stop_event = threading.Event()
        self.error = None
        self.writer_thread = None
        self.bytes_written = 0
    
    def start(self):
        """Start background writing thread."""
        # Ensure parent directory exists
        Path(self.file_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.writer_thread = threading.Thread(target=self._write_loop, daemon=True)
        self.writer_thread.start()
    
    def _write_loop(self):
        """Background thread that writes queued data."""
        try:
            with open(self.file_path, 'wb') as f:
                while not self.stop_event.is_set():
                    try:
                        chunk = self.data_queue.get(timeout=QUEUE_TIMEOUT)
                        if chunk is None:
                            # Sentinel - stop writing
                            self.data_queue.task_done()
                            break
                        
                        f.write(chunk)
                        self.bytes_written += len(chunk)
                        self.data_queue.task_done()
                    
                    except queue.Empty:
                        continue
        
        except Exception as e:
            self.error = e
    
    def write(self, data: bytes, timeout: Optional[float] = None):
        """
        Queue data for writing.
        
        Args:
            data: Bytes to write
            timeout: Max seconds to wait if queue full
        """
        try:
            self.data_queue.put(data, timeout=timeout)
        except queue.Full:
            raise IOError("Write queue full - data loss possible")
    
    def finish(self, timeout: float = 10.0):
        """
        Signal end of writing and wait for completion.
        
        Args:
            timeout: Max seconds to wait for writes to complete
        """
        # Send sentinel
        self.data_queue.put(None)
        
        # Wait for queue to empty
        self.data_queue.join()
        
        # Wait for thread to finish
        if self.writer_thread:
            self.writer_thread.join(timeout=timeout)
        
        if self.error:
            raise self.error
    
    def stop(self):
        """Stop writing thread (may lose data)."""
        self.stop_event.set()
        if self.writer_thread:
            self.writer_thread.join(timeout=2.0)
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.finish()
        else:
            self.stop()


class ThreadedFileOperations:
    """
    Parallel file operations using thread pools.
    
    Copy, move, verify, and process files using multiple threads.
    """
    
    def __init__(
        self,
        max_workers: int = DEFAULT_MAX_WORKERS,
        log_callback: Optional[Callable[[str], None]] = None
    ):
        """
        Initialize threaded file operations.
        
        Args:
            max_workers: Maximum concurrent operations
            log_callback: Optional logging callback
        """
        self.max_workers = max_workers
        self.log_callback = log_callback or print
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def _log(self, message: str):
        """Log message via callback."""
        if self.log_callback:
            self.log_callback(message)
    
    def copy_file(
        self,
        src: str,
        dst: str,
        buffer_size: int = DEFAULT_BUFFER_SIZE
    ) -> int:
        """
        Copy file with buffered I/O.
        
        Args:
            src: Source file path
            dst: Destination file path
            buffer_size: Buffer size for copying
        
        Returns:
            Bytes copied
        """
        # Ensure destination directory exists
        Path(dst).parent.mkdir(parents=True, exist_ok=True)
        
        bytes_copied = 0
        with open(src, 'rb') as fsrc:
            with open(dst, 'wb') as fdst:
                while True:
                    chunk = fsrc.read(buffer_size)
                    if not chunk:
                        break
                    fdst.write(chunk)
                    bytes_copied += len(chunk)
        
        return bytes_copied
    
    def copy_files_parallel(
        self,
        file_pairs: List[Tuple[str, str]],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[Tuple[str, bool, Optional[str]]]:
        """
        Copy multiple files in parallel.
        
        Args:
            file_pairs: List of (source, destination) tuples
            progress_callback: Optional callback(completed, total)
        
        Returns:
            List of (file, success, error_message) tuples
        """
        self._log(f"[Threaded I/O] Starting parallel copy of {len(file_pairs)} files...")
        
        results = []
        completed = 0
        
        # Submit all copy operations
        futures = {
            self.executor.submit(self._copy_with_error_handling, src, dst): (src, dst)
            for src, dst in file_pairs
        }
        
        # Process as they complete
        for future in as_completed(futures):
            src, dst = futures[future]
            try:
                bytes_copied = future.result()
                results.append((src, True, None))
                self._log(f"[Threaded I/O] ✓ Copied: {Path(src).name} ({bytes_copied} bytes)")
            except Exception as e:
                results.append((src, False, str(e)))
                self._log(f"[Threaded I/O] ✗ Failed: {Path(src).name} - {e}")
            
            completed += 1
            if progress_callback:
                progress_callback(completed, len(file_pairs))
        
        self._log(f"[Threaded I/O] Copy complete: {sum(1 for _, ok, _ in results if ok)}/{len(file_pairs)} successful")
        return results
    
    def _copy_with_error_handling(self, src: str, dst: str) -> int:
        """Wrapper for copy_file with proper error handling."""
        return self.copy_file(src, dst)
    
    def verify_file(self, file_path: str, checksum: Optional[str] = None) -> bool:
        """
        Verify file integrity via checksum.
        
        Args:
            file_path: Path to file
            checksum: Optional SHA256 checksum to verify against
        
        Returns:
            True if valid, False otherwise
        """
        if not os.path.exists(file_path):
            return False
        
        if checksum is None:
            # Just verify file exists and is readable
            try:
                with open(file_path, 'rb') as f:
                    f.read(1)  # Try reading first byte
                return True
            except Exception:
                return False
        
        # Verify checksum
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(DEFAULT_BUFFER_SIZE)
                if not chunk:
                    break
                sha256.update(chunk)
        
        return sha256.hexdigest() == checksum
    
    def verify_files_parallel(
        self,
        files: List[str],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[Tuple[str, bool]]:
        """
        Verify multiple files in parallel.
        
        Args:
            files: List of file paths to verify
            progress_callback: Optional callback(completed, total)
        
        Returns:
            List of (file, is_valid) tuples
        """
        self._log(f"[Threaded I/O] Verifying {len(files)} files...")
        
        results = []
        completed = 0
        
        futures = {
            self.executor.submit(self.verify_file, file_path): file_path
            for file_path in files
        }
        
        for future in as_completed(futures):
            file_path = futures[future]
            try:
                is_valid = future.result()
                results.append((file_path, is_valid))
                status = "✓" if is_valid else "✗"
                self._log(f"[Threaded I/O] {status} {Path(file_path).name}")
            except Exception as e:
                results.append((file_path, False))
                self._log(f"[Threaded I/O] ✗ {Path(file_path).name} - {e}")
            
            completed += 1
            if progress_callback:
                progress_callback(completed, len(files))
        
        valid_count = sum(1 for _, valid in results if valid)
        self._log(f"[Threaded I/O] Verification complete: {valid_count}/{len(files)} valid")
        return results
    
    def delete_files_parallel(
        self,
        files: List[str],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[Tuple[str, bool]]:
        """
        Delete multiple files in parallel.
        
        Args:
            files: List of file paths to delete
            progress_callback: Optional callback(completed, total)
        
        Returns:
            List of (file, success) tuples
        """
        self._log(f"[Threaded I/O] Deleting {len(files)} files...")
        
        results = []
        completed = 0
        
        def delete_file(path: str) -> bool:
            try:
                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                return True
            except Exception:
                return False
        
        futures = {
            self.executor.submit(delete_file, file_path): file_path
            for file_path in files
        }
        
        for future in as_completed(futures):
            file_path = futures[future]
            success = future.result()
            results.append((file_path, success))
            
            status = "✓" if success else "✗"
            self._log(f"[Threaded I/O] {status} Deleted: {Path(file_path).name}")
            
            completed += 1
            if progress_callback:
                progress_callback(completed, len(files))
        
        success_count = sum(1 for _, ok in results if ok)
        self._log(f"[Threaded I/O] Deletion complete: {success_count}/{len(files)} deleted")
        return results
    
    def shutdown(self, wait: bool = True):
        """Shutdown thread pool."""
        self.executor.shutdown(wait=wait)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()


# Convenience functions
def async_copy_file(
    src: str,
    dst: str,
    progress_callback: Optional[Callable[[float], None]] = None
) -> int:
    """
    Copy file asynchronously with progress tracking.
    
    Args:
        src: Source file
        dst: Destination file
        progress_callback: Optional callback(percent_complete)
    
    Returns:
        Bytes copied
    """
    total_size = os.path.getsize(src)
    bytes_copied = 0
    
    with AsyncFileReader(src) as reader, AsyncFileWriter(dst) as writer:
        while True:
            chunk = reader.read(timeout=5.0)
            if chunk is None:
                break
            
            writer.write(chunk)
            bytes_copied += len(chunk)
            
            if progress_callback:
                progress_callback((bytes_copied / total_size) * 100.0)
    
    return bytes_copied


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Threaded I/O Operations Test")
    parser.add_argument("--test", action="store_true", help="Run performance test")
    parser.add_argument("--bench", action="store_true", help="Benchmark threaded vs single-threaded")
    
    args = parser.parse_args()
    
    if args.test:
        print("="*60)
        print("Threaded I/O Test")
        print("="*60 + "\n")
        
        # Create test file
        test_file = "test_threaded_io.bin"
        test_size = 50 * 1024 * 1024  # 50MB
        
        print(f"[Test] Creating {test_size/(1024*1024):.0f}MB test file...")
        with open(test_file, 'wb') as f:
            f.write(os.urandom(test_size))
        
        # Test async copy
        print("\n[Test] Testing async copy...")
        start = time.time()
        
        def progress(pct):
            if int(pct) % 10 == 0:
                print(f"  Progress: {pct:.0f}%")
        
        bytes_copied = async_copy_file(test_file, "test_copy.bin", progress)
        elapsed = time.time() - start
        
        print(f"[Test] Copied {bytes_copied/(1024*1024):.2f}MB in {elapsed:.2f}s")
        print(f"[Test] Speed: {(bytes_copied/1024/1024)/elapsed:.2f} MB/s")
        
        # Cleanup
        os.remove(test_file)
        os.remove("test_copy.bin")
        
        print("\n[OK] Test complete!")
    
    elif args.bench:
        print("="*60)
        print("Threaded I/O Benchmark")
        print("="*60 + "\n")
        
        # Create test files
        test_dir = "test_bench"
        os.makedirs(test_dir, exist_ok=True)
        
        file_count = 20
        file_size = 10 * 1024 * 1024  # 10MB each
        
        print(f"[Bench] Creating {file_count} test files ({file_size/(1024*1024):.0f}MB each)...")
        test_files = []
        for i in range(file_count):
            file_path = os.path.join(test_dir, f"test_{i}.bin")
            with open(file_path, 'wb') as f:
                f.write(os.urandom(file_size))
            test_files.append(file_path)
        
        # Benchmark single-threaded
        print("\n[Bench] Single-threaded copy...")
        start = time.time()
        for src in test_files:
            shutil.copy(src, src + ".copy1")
        single_time = time.time() - start
        print(f"  Time: {single_time:.2f}s")
        
        # Benchmark multi-threaded
        print("\n[Bench] Multi-threaded copy (4 workers)...")
        file_pairs = [(src, src + ".copy2") for src in test_files]
        
        with ThreadedFileOperations(max_workers=4) as ops:
            start = time.time()
            ops.copy_files_parallel(file_pairs)
            threaded_time = time.time() - start
        
        print(f"  Time: {threaded_time:.2f}s")
        
        speedup = single_time / threaded_time
        print(f"\n[Bench] Speedup: {speedup:.2f}x faster with threading")
        
        # Cleanup
        shutil.rmtree(test_dir)
        
        print("\n[OK] Benchmark complete!")
    
    else:
        parser.print_help()
