# coding=utf-8
"""
Harvests all comments from all posts on a Facebook page and writes
them to a file. No metadata, just raw comment text separated by \n.
I don't know why the sum of all "total_count" fields returned from
the FB API, are greater than the number of comments we are able to
download. It confuses me and now this project bores me. Fork away.

"""

from sys import stdout
import requests
import facebook

# Change stuff here!
TOKEN = "[YOUR API ACCESS TOKEN HERE]"
PAGE = "[PAGE TO SCRAPE]"
FILENAME = "output.txt"
GRAPH = facebook.GraphAPI(TOKEN)


def progress(count, total):
    """Show progress bar."""
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    prog_bar = '#' * filled_len + '-' * (bar_len - filled_len)

    stdout.write(
        '[%s] %s%s (%s/%s)\r' %
        (prog_bar, int(percents), '%', count, total))
    stdout.flush()


def cursor_up():
    """Move cursor up and clear line."""
    stdout.write("\033[F")  # back to previous line.
    stdout.write("\033[K")  # clear line.


def get_posts():
    """Return list of all post IDs on page."""
    posts = GRAPH.get_connections(PAGE, "posts", limit=25)
    allposts = []

    # Looper igennem pages:
    while True:
        try:
            for post in posts["data"]:
                allposts.append(post["id"].encode("utf-8"))
            # Try accessing the next page, if it exists.
            posts = requests.get(posts["paging"]["next"]).json()
            print "Counting posts: %s" % len(allposts)
            cursor_up()

        except KeyError:
            # When there are no more pages (["paging"]["next"]), break.
            print "Total posts: %s" % len(allposts)
            break

    return allposts


def count_comments(allposts):
    """Count number of comments from list of posts."""
    count = 0
    for post in allposts:
        summary = GRAPH.get_connections(post, "comments",
                                        filter="stream",
                                        summary="true",
                                        fields="total_count",
                                        limit=0)

        count += summary["summary"]["total_count"]
        print "Counting comments: %s" % count
        cursor_up()

    print "Total comments: %s" % count
    return count


def scrape_post(post_id, total):
    """Scrape all comments on a post and print progress."""
    comments = GRAPH.get_connections(post_id, "comments",
                                     filter="stream",
                                     limit=250)
    postcomments = []

    # Loop through pages:
    while True:

        try:
            for comment in comments["data"]:
                postcomments.append(comment["message"].encode("utf-8"))
                progress((len(postcomments) + total), NUMBER_OF_COMMENTS)

            # Try accessing the next page, if it exists.
            comments = requests.get(comments["paging"]["next"]).json()

        except KeyError:
            # When there are no more pages (["paging"]["next"]), break.
            break

    return postcomments


print "Getting metadata:"

# Collect all post IDs in a list
ALL_POSTS = get_posts()

# Count comments on all posts
NUMBER_OF_COMMENTS = count_comments(ALL_POSTS)

# Make list for collection of comments content
FINAL_COMMENTS = []

print "Downloading comments:"
# Loop through list of posts and scrape comments
for post in ALL_POSTS:
    for comment in scrape_post(post, len(FINAL_COMMENTS)):
        FINAL_COMMENTS.append(comment)

# Writing each comment to a seperate line in a file
print "Writing to file"

F = open(FILENAME, "w")
for idx, comment in enumerate(FINAL_COMMENTS):
    F.write(comment + "\n")
    progress(idx, NUMBER_OF_COMMENTS)
    cursor_up()

F.close()

print
print "Done."
