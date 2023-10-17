from collections import defaultdict

import praw
from config import CLIENT_ID, CLIENT_SECRET
from praw.models import MoreComments
from preprocessing import segment_text

noise = [
    "hello, users of cmv! this is a footnote from your moderators",
    "comment has been remove",
    "comment has been automatically removed",
    "if you would like to appeal, please message the moderators by clicking this link.",
    "this comment has been overwritten by an open source script to protect",
    "then simply click on your username on reddit, go to the comments tab, scroll down as far as possibe (hint:use res), and hit the new overwrite button at the top.",
    "reply to their comment with the delta symbol",
]


class Reddit:
    def __init__(self):
        self.client = praw.Reddit(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            user_agent="frame-explorer",
        )

    def extract_comments(self, comments, limit=None, threshold=0):
        comments.replace_more(limit=limit, threshold=threshold)
        comments = comments.list()
        depths = defaultdict(list)
        for comment in comments:
            lower_text = comment.body.lower()
            author = comment.author
            if author is not None:
                author = author.name
            if comment.stickied:
                continue
            if isinstance(comment, MoreComments):
                continue
            if author in ["DeltaBot"]:
                continue
            if any(e in lower_text for e in noise):
                continue
            reply_ids = [
                e.id for e in comment.replies if not isinstance(e, MoreComments)
            ]
            depths[comment.depth].append(
                {
                    "id": comment.id,
                    "name": comment.name,
                    "parent": comment.parent_id,
                    "author": author,
                    "text": segment_text(comment.body_html),
                    "replies": reply_ids,
                    "is_submitter": comment.is_submitter,
                }
            )
        # remove comments that have no parent anymore
        extracted = []
        removed = []
        this_level_ids = set()
        for depth, level_comments in sorted(depths.items(), key=lambda x: x[0]):
            next_level_ids = set()
            for comment in level_comments:
                if depth == 0 or comment["id"] in this_level_ids:
                    extracted.append(comment)
                    next_level_ids.update(comment["replies"])
                else:
                    removed.append(comment)
            this_level_ids = next_level_ids
        del comment["replies"]
        return extracted

    def get_thread(self, url, limit=None, threshold=0):
        submission = self.client.submission(url=url)
        author = submission.author
        if author is not None:
            author = author.name
        comments = self.extract_comments(
            submission.comments, limit=limit, threshold=threshold
        )
        thread = {
            "url": f"https://www.reddit.com/{submission.id}",
            "title": submission.title,
            "root": {
                "id": submission.id,
                "name": submission.name,
                "parent": None,
                "author": author,
                "text": segment_text(submission.selftext_html),
                "is_submitter": True,
            },
            "num_comments": len(comments) - 1,
            "comments": comments,
        }
        return thread
