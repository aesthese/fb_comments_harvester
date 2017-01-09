# coding=utf-8
import facebook
import requests

token = "[INSERT API ACCESS TOKEN HERE]"
graph = facebook.GraphAPI(token)
page = "[NAME OF PAGE TO SCRAPE]"
filnavn = "output.txt"


def cursor_up():
    print "\x1b[2K\r",


def get_posts():
    posts = graph.get_connections(page, "posts", limit=25)
    allposts = []

    print "Getting all posts..."
    # Looper igennem pages:
    while (True):
        try:
            for post in posts["data"]:
                print post["id"].encode("utf-8")
                allposts.append(post["id"].encode("utf-8"))

def cursor_up():
    stdout.write("\033[F")  # back to previous line.
    #stdout.write("\033[K")  #clear line.


def get_posts():
    posts = graph.get_connections(page, "posts", limit=25)
    allposts = []

    print "Getting all posts..."
    # Looper igennem pages:
    while (True):
        try:
            for post in posts["data"]:
                allposts.append(post["id"].encode("utf-8"))
            # Forsøg at tilgå data på næste page, hvis den findes.
            posts = requests.get(posts["paging"]["next"]).json()
            print "%s posts on page" % len(allposts)
            cursor_up()
        except KeyError:
            # Når der ikke er flere pages (["paging"]["next"]), break fra loopet.
            print "%s posts on page" % len(allposts)
            break
    return allposts


def get_comments(post_id):
    comments = graph.get_connections(post_id, "comments", limit=250)
    allcomments = []

    # Looper igennem pages:
    while (True):

        try:
            for comment in comments["data"]:
                allcomments.append(comment["message"].encode("utf-8"))
            # Forsøg at tilgå data på næste page, hvis den findes.
            comments = requests.get(comments["paging"]["next"]).json()
            print "Getting %s comments from post: %s" % (len(allcomments), post_id)
            cursor_up()

        except KeyError:
            # Når der ikke er flere pages (["paging"]["next"]), break fra loopet.
            break
    return allcomments


final_comments = []
for post in get_posts():
    print "Current post: %s" % post
    print "TOTAL COMMENTS: %s" % len(final_comments)
    cursor_up()
    cursor_up()

    for comment in get_comments(post):
        final_comments.append(comment)




print "SKRIVER TIL FIL"

f = open(filnavn, "w")
count = 0
for comment in final_comments:
    count += 1
    f.write(comment + "\n")
    print "skrevet %s linjer" % count
    cursor_up()
f.close()

print
print "Done."
