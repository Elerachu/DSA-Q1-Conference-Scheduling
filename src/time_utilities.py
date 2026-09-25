# This file turns a time string like "11:00" into a number because numbers are much easier to compare and sort than text.

def time_to_minutes(time_str):
    """
    Converts a time string like '11:00' into total minutes since midnight.
    Example: '11:00' = 660   (because 11 hours * 60 = 660 minutes)
    """

    # split("​:") breaks the string at the colon.
    # "11:20" becomes the list ["11", "20"]
    hours, minutes = time_str.split(":")

    # hours and minutes are currently STRINGS
    # int() converts them into real numbers I can do the math with.
    # int() also safely handles the leading zero so "09" becomes 9 and not an error.
    hours = int(hours)
    minutes = int(minutes)

    # 1 hour = 60 minutes so multiply hours by 60, then add the minutes part.
    total_minutes = hours * 60 + minutes

    return total_minutes


# This block only runs if I execute this file DIRECTLY and not when it's imported
# by another file. This is a good way to leave quick tests inside the file itself.
if __name__ == "__main__":
    # Quick manual test: Run this file on its own to check the function works.
    print(time_to_minutes("09:00"))   # print 540
    print(time_to_minutes("10:00"))   # print 600
    print(time_to_minutes("22:50"))   # print 1370