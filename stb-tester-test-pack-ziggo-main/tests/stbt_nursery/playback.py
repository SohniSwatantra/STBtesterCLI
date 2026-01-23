# Copyright 2017-2020 Stb-tester.com Ltd.
# encoding: utf-8

import queue
import sys
import time
from multiprocessing.pool import ThreadPool

import cv2
import stbt
import stbt.audio


def wait_for_content_start(
        keypress=None, spinner_fn=None, mask=None, timeout_secs=30):
    """
    Waits for content to start taking measurements as it goes.  It expects the
    sequence to go

    keypress ------> Goes black ------> No longer black----¬
             L--> Spinner appears ---> Spinner disappears--¬
             L---------------> Sound ----------------------¬
             L---------------> Motion ---------------------L---> Done

    Arguments:

    * keypress - A `stbt.Keypress` indicating the keypress that caused the
      content to start.
    * spinner_fn - Function taking a frame argument and returning an value that
      is Truthy if the spinner is visible in this frame, Falsey otherwise or
      None for no spinner detection.
    * mask - A mask used for motion and black detection. This should mask out
      the spinner and any UI elements superimposed on the video.
    * timeout_secs: Number of seconds to wait for content to start playing.

    Returns:

    * A list of 3 element tuples (time, event_type, event) in time order.
      Possible event types are: "press", "motion", "black", "not_black",
      "spinner", "not_spinner", "audio"
    """
    events = []
    if keypress:
        events.append((keypress.start_time, "press", keypress))
    else:
        events.append((time.time(), "start", None))

    if mask is not None:
        mask = stbt.load_image(mask, cv2.IMREAD_GRAYSCALE)

    pool = _ThreadPool()

    @pool.add
    def _watch_motion():
        def frames():
            for frame in stbt.frames():
                yield frame
                pool.raise_for_stop()

        r = stbt.wait_for_motion(mask=mask, timeout_secs=timeout_secs,
                                 consecutive_frames="5/20", frames=frames())
        events.append((r.time, "motion", r))

    @pool.add
    def _watch_black():
        frames = stbt.frames(timeout_secs=timeout_secs)
        for f in frames:
            b = stbt.is_screen_black(f, mask=mask, threshold=40)
            if b:
                events.append((f.time, "black", b))
                break
            pool.raise_for_stop()
        else:
            return

        for f in frames:
            b = stbt.is_screen_black(f, mask=mask, threshold=40)
            if not b:
                events.append((f.time, "not_black", b))
                break
            pool.raise_for_stop()
        else:
            return

    if spinner_fn:
        @pool.add
        def _watch_spinner():
            frames = stbt.frames(timeout_secs=timeout_secs)
            for f in frames:
                spinner = spinner_fn(frame=f)
                if spinner:
                    events.append((f.time, "spinner", spinner))
                    break
                pool.raise_for_stop()
            else:
                return

            for f in frames:
                spinner = spinner_fn(frame=f)
                if not spinner:
                    events.append((f.time, "not_spinner", spinner))
                    return
                pool.raise_for_stop()

    @pool.add
    def _listen():
        r = stbt.audio.wait_for_volume_change(timeout_secs=timeout_secs)
        events.append((r.time, "audio", r))

    pool.run()

    events.sort()
    return events


class _ThreadPool(object):
    class Stop(BaseException):
        pass

    def __init__(self):
        self._fns = []
        self._stop = False

        # We implement our own exception forwarding here because ThreadPool
        # doesn't preserve tracebacks.
        self._results = queue.Queue()

    def add(self, fn, *args):
        self._fns.append((fn, args))

    def raise_for_stop(self):
        if self._stop:
            raise _ThreadPool.Stop()

    def run(self):
        pool = ThreadPool(processes=len(self._fns))
        try:
            # This will raise if one of the threads raised
            pool.map_async(self._call, self._fns,
                           callback=lambda _: self._results.put(None))
            exc = self._results.get()
            if exc:
                raise exc[1].with_traceback(exc[2])
        finally:
            self._stop = True
            pool.close()
            pool.join()

    def _call(self, fn_and_args):
        try:
            fn_and_args[0](*fn_and_args[1])
        except _ThreadPool.Stop:
            pass
        except Exception:  # pylint: disable=broad-except
            self._results.put(sys.exc_info())
