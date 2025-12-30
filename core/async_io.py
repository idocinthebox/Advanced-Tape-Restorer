"""
Asynchronous I/O for Video Processing
Non-blocking file operations for better performance

Features:
- Async file reading/writing
- Background I/O operations
- I/O pooling for batch operations
- Progress tracking
"""

import asyncio
import aiofiles
from pathlib import Path
from typing import List, Optional, Callable, Any
from concurrent.futures import ThreadPoolExecutor
import threading
import queue


class AsyncFileReader:
    """
    Asynchronous file reader for video frames.

    Reads ahead while processing continues, eliminating I/O wait time.

    Usage:
        async with AsyncFileReader(file_path) as reader:
            async for data in reader:
                process(data)
    """

    def __init__(self, file_path: Path, chunk_size: int = 4 * 1024 * 1024, buffer_size: int = 10):
        """
        Initialize async reader.

        Args:
            file_path: Path to file
            chunk_size: Bytes per read operation (default 4MB for video files)
            buffer_size: Number of chunks to buffer (read-ahead)
        """
        self.file_path = Path(file_path)
        self.chunk_size = chunk_size
        self.buffer_size = buffer_size

    async def __aenter__(self):
        """Async context manager entry."""
        self.file = await aiofiles.open(self.file_path, mode="rb")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.file.close()

    async def read_chunk(self) -> Optional[bytes]:
        """Read one chunk."""
        data = await self.file.read(self.chunk_size)
        return data if data else None

    async def __aiter__(self):
        """Async iterator."""
        return self

    async def __anext__(self):
        """Get next chunk."""
        data = await self.read_chunk()
        if data is None:
            raise StopAsyncIteration
        return data


class AsyncFileWriter:
    """
    Asynchronous file writer with buffering.

    Writes happen in background while processing continues.

    Usage:
        async with AsyncFileWriter(output_path) as writer:
            await writer.write(data)
    """

    def __init__(self, file_path: Path, buffer_size: int = 100):
        """
        Initialize async writer.

        Args:
            file_path: Output file path
            buffer_size: Number of writes to buffer
        """
        self.file_path = Path(file_path)
        self.buffer_size = buffer_size
        self.write_queue = asyncio.Queue(maxsize=buffer_size)
        self.writer_task = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.file = await aiofiles.open(self.file_path, mode="wb")

        # Start background writer
        self.writer_task = asyncio.create_task(self._writer_loop())

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        # Signal end of writes
        await self.write_queue.put(None)

        # Wait for writer to finish
        if self.writer_task:
            await self.writer_task

        await self.file.close()

    async def _writer_loop(self):
        """Background loop that performs writes."""
        while True:
            data = await self.write_queue.get()

            if data is None:  # Stop signal
                break

            await self.file.write(data)

    async def write(self, data: bytes):
        """Queue data for writing."""
        await self.write_queue.put(data)


class AsyncBatchProcessor:
    """
    Process multiple files concurrently.

    Usage:
        processor = AsyncBatchProcessor(max_concurrent=4)
        await processor.process_batch(files, process_func)
    """

    def __init__(self, max_concurrent: int = 4):
        """
        Initialize batch processor.

        Args:
            max_concurrent: Maximum concurrent operations
        """
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def process_file(
        self, file_path: Path, process_func: Callable, **kwargs
    ) -> Any:
        """
        Process single file.

        Args:
            file_path: File to process
            process_func: Processing function (can be sync or async)
            **kwargs: Additional arguments to process_func

        Returns:
            Result from process_func
        """
        async with self.semaphore:
            # Check if function is async
            if asyncio.iscoroutinefunction(process_func):
                result = await process_func(file_path, **kwargs)
            else:
                # Run sync function in thread pool
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None, lambda: process_func(file_path, **kwargs)
                )

            return result

    async def process_batch(
        self,
        file_paths: List[Path],
        process_func: Callable,
        progress_callback: Optional[Callable] = None,
        **kwargs,
    ) -> List[Any]:
        """
        Process multiple files concurrently.

        Args:
            file_paths: List of files to process
            process_func: Function to apply to each file
            progress_callback: Optional callback(completed, total)
            **kwargs: Additional arguments to process_func

        Returns:
            List of results
        """
        tasks = []
        for file_path in file_paths:
            task = self.process_file(file_path, process_func, **kwargs)
            tasks.append(task)

        # Process with progress tracking
        results = []
        completed = 0

        for coro in asyncio.as_completed(tasks):
            result = await coro
            results.append(result)

            completed += 1
            if progress_callback:
                progress_callback(completed, len(file_paths))

        return results


class BackgroundIOPool:
    """
    Thread pool for blocking I/O operations.

    Prevents blocking the main event loop with sync I/O.

    Usage:
        pool = BackgroundIOPool(workers=4)
        result = pool.submit(read_file, "path.txt")
        data = result.result()
    """

    def __init__(self, workers: int = 4):
        """
        Initialize I/O pool.

        Args:
            workers: Number of worker threads
        """
        self.executor = ThreadPoolExecutor(max_workers=workers)
        print(f"Background I/O pool initialized with {workers} workers")

    def submit(self, func: Callable, *args, **kwargs):
        """
        Submit I/O operation to pool.

        Args:
            func: Function to execute
            *args: Arguments to function
            **kwargs: Keyword arguments

        Returns:
            Future object
        """
        return self.executor.submit(func, *args, **kwargs)

    def map(self, func: Callable, items: List[Any]) -> List[Any]:
        """
        Map function over items in parallel.

        Args:
            func: Function to apply
            items: Items to process

        Returns:
            List of results
        """
        return list(self.executor.map(func, items))

    def shutdown(self, wait: bool = True):
        """Shutdown the pool."""
        self.executor.shutdown(wait=wait)


class AsyncStreamProcessor:
    """
    Process video frames as a stream (producer-consumer).

    Decouples reading, processing, and writing for maximum throughput.
    """

    def __init__(self, buffer_size: int = 50):
        """
        Initialize stream processor.

        Args:
            buffer_size: Size of internal buffers
        """
        self.read_queue = asyncio.Queue(maxsize=buffer_size)
        self.process_queue = asyncio.Queue(maxsize=buffer_size)
        self.write_queue = asyncio.Queue(maxsize=buffer_size)

    async def reader(self, source, stop_event):
        """Read frames and queue them."""
        idx = 0
        while not stop_event.is_set():
            # Read frame (implement your frame reading logic)
            frame = await self._read_frame(source, idx)

            if frame is None:
                break

            await self.read_queue.put((idx, frame))
            idx += 1

        # Signal end
        await self.read_queue.put(None)

    async def processor(self, process_func, stop_event):
        """Process frames from queue."""
        while not stop_event.is_set():
            item = await self.read_queue.get()

            if item is None:  # End signal
                await self.process_queue.put(None)
                break

            idx, frame = item

            # Process (run in thread pool if sync function)
            if asyncio.iscoroutinefunction(process_func):
                result = await process_func(frame)
            else:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, process_func, frame)

            await self.process_queue.put((idx, result))

    async def writer(self, destination, stop_event):
        """Write processed frames."""
        while not stop_event.is_set():
            item = await self.process_queue.get()

            if item is None:  # End signal
                break

            idx, frame = item

            # Write frame (implement your writing logic)
            await self._write_frame(destination, idx, frame)

    async def _read_frame(self, source, idx):
        """Placeholder for frame reading logic."""
        # Implement based on your video library
        await asyncio.sleep(0.001)  # Simulate I/O
        return f"frame_{idx}" if idx < 100 else None

    async def _write_frame(self, destination, idx, frame):
        """Placeholder for frame writing logic."""
        # Implement based on your video library
        await asyncio.sleep(0.001)  # Simulate I/O

    async def run(self, source, destination, process_func):
        """
        Run the full pipeline.

        Args:
            source: Input source
            destination: Output destination
            process_func: Processing function
        """
        stop_event = asyncio.Event()

        # Start all components
        reader_task = asyncio.create_task(self.reader(source, stop_event))
        processor_task = asyncio.create_task(self.processor(process_func, stop_event))
        writer_task = asyncio.create_task(self.writer(destination, stop_event))

        # Wait for completion
        await asyncio.gather(reader_task, processor_task, writer_task)


# Example usage
async def example_async_batch():
    """Example: Process multiple files concurrently."""

    async def process_file(file_path: Path):
        """Simulated file processing."""
        await asyncio.sleep(0.1)  # Simulate work
        return f"Processed: {file_path.name}"

    def progress_callback(completed, total):
        """Progress callback."""
        print(f"Progress: {completed}/{total} files")

    # Create processor
    processor = AsyncBatchProcessor(max_concurrent=4)

    # Simulate file list
    files = [Path(f"file_{i}.mp4") for i in range(20)]

    # Process batch
    results = await processor.process_batch(
        files, process_file, progress_callback=progress_callback
    )

    print(f"\nProcessed {len(results)} files")


async def example_stream_processing():
    """Example: Stream processing pipeline."""

    def process_frame(frame):
        """Frame processing function."""
        return f"processed_{frame}"

    # Create pipeline
    pipeline = AsyncStreamProcessor(buffer_size=10)

    # Run
    await pipeline.run(
        source="input.mp4", destination="output.mp4", process_func=process_frame
    )


if __name__ == "__main__":
    print("=== Async I/O Test ===\n")

    # Test batch processing
    print("Testing async batch processing...")
    asyncio.run(example_async_batch())

    print("\n\nTesting stream processing...")
    asyncio.run(example_stream_processing())

    print("\n✓ Async I/O tests complete")
