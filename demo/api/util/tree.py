def thread_to_tree(thread):
    tree = thread.copy()
    post_dict = {
        comment["name"]: comment | {"comments": []} for comment in tree.pop("comments")
    }
    root = tree["root"].copy()
    root["comments"] = []
    tree["root"] = root
    tree["labels"] = {}
    tree["frames"] = {}
    tree["meta"] = {}
    post_dict[root["name"]] = root

    for post in post_dict.values():
        parent_id = post.get("parent")
        if parent_id:
            post_dict[parent_id]["comments"].append(post)

    return tree
