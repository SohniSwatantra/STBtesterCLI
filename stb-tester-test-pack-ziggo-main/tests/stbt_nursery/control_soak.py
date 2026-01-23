# Copyright 2019 Stb-tester.com Ltd.

import os

import cv2
import numpy
import stbt


def soak_remote_control(
        key_next="KEY_RIGHT", key_prev="KEY_LEFT",
        region=stbt.Region.ALL, mask=None, count=100,
        interpress_delay_secs=None):
    """
    Reliability test for Stb-tester's remote control emulation.

    Press KEY_RIGHT and KEY_LEFT 100 times (50 times each), and make sure they
    have an effect each time. We take two screenshots after the first RIGHT &
    LEFT keypresses, and we use those screenshots to verify that each
    subsequent keypress has landed in the expected state. This should be
    sufficient to detect intermittent missed keypresses and double presses.

    Use ``region`` and/or ``mask`` to exclude parts of the page that might
    change independently of keypresses, such as picture-in-picture video or a
    clock.
    """
    if mask is None:
        m = stbt.crop(
            numpy.ones(stbt.get_frame().shape[:2], dtype=numpy.uint8) * 255,
            region)
    else:
        m = stbt.load_image(mask, cv2.IMREAD_GRAYSCALE)

    # Get in a position where we'll be able to press left later. Note: no
    # assertion - it's ok if we can't move right right now
    stbt.press(key_next)
    stbt.press_and_wait(key_next, region=region, mask=m)  # pylint:disable=stbt-unused-return-value

    # Grab reference images of the left and right position. We need these to
    # check that we've actually moved, and haven't moved too far. We add an
    # alpha channel (transparency) using the user-supplied mask.
    right_template = numpy.append(stbt.crop(stbt.get_frame(), region),
                                  m[:, :, numpy.newaxis],
                                  axis=2)
    cv2.imwrite("right_template.png", right_template)

    if stbt.press_and_wait(key_prev, region=region, mask=m).status == \
            stbt.TransitionStatus.START_TIMEOUT:
        raise RuntimeError(
            "No movement after pressing %r during setup" % (key_prev,))
    if stbt.match(right_template, region=region):
        raise RuntimeError(
            "Setup error: No detectable differences after pressing %r"
            % (key_prev,))
    left_template = numpy.append(stbt.crop(stbt.get_frame(), region),
                                 m[:, :, numpy.newaxis],
                                 axis=2)
    cv2.imwrite("left_template.png", left_template)

    # Error messages:
    missed_msg = "Missed keypress: No change after pressing %s"
    double_msg = \
        "Didn't find expected screen after pressing %s (double keypress?)"

    # Now we perform the actual test:
    for i in range(count):

        if i % 2 == 0:
            key, expected, unchanged = key_next, right_template, left_template
        else:
            key, expected, unchanged = key_prev, left_template, right_template

        stbt.press(key, interpress_delay_secs)
        if not stbt.wait_until(lambda: stbt.match(expected, region=region)):  # pylint:disable=cell-var-from-loop
            if stbt.match(unchanged, region=region):
                raise AssertionError(missed_msg % key)
            else:
                raise AssertionError(double_msg % key)

    # Only save the reference images for debugging if the test failed.
    os.remove("right_template.png")  # pylint:disable=stbt-missing-image
    os.remove("left_template.png")  # pylint:disable=stbt-missing-image
