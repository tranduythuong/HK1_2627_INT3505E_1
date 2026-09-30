1. Resources: users, posts, profiles, comments, tags, follows
2. Phân loại Collection / Item / Sub-resource
_______________Collection_____________--
/users
/posts
/comments
/tags

_______________Item____________________
/users/{user_id}
/posts/{post_id}
/comments/{comment_id}
/tags/{tag_id}

_______________Sub-resource______________
/users/{user_id}/profile
/users/{user_id}/posts
/users/{user_id}/followers
/users/{user_id}/following

/posts/{post_id}/comments
/posts/{post_id}/tags
3. Version segment
GET/api/v1/posts	
POS/api/v1/posts
___________________


```mermaid
flowchart TD
    API["/api/v1"]

    API --> USERS["/users"]
    API --> POSTS["/posts"]
    API --> COMMENTS["/comments"]
    API --> TAGS["/tags"]

    %% USERS
    USERS --> USERS_GET["GET /users"]
    USERS --> USERS_POST["POST /users"]
    USERS --> USER_ID["/users/{user_id}"]

    USER_ID --> USER_GET["GET"]
    USER_ID --> USER_PUT["PUT"]
    USER_ID --> USER_PATCH["PATCH"]
    USER_ID --> USER_DELETE["DELETE"]
    USER_ID --> PROFILE["/profile"]
    USER_ID --> USER_POSTS["/posts"]
    USER_ID --> FOLLOWERS["/followers"]
    USER_ID --> FOLLOWING["/following"]

    %% POSTS
    POSTS --> POSTS_GET["GET /posts"]
    POSTS --> POSTS_POST["POST /posts"]
    POSTS --> POST_ID["/posts/{post_id}"]

    POST_ID --> POST_GET["GET"]
    POST_ID --> POST_PUT["PUT"]
    POST_ID --> POST_PATCH["PATCH"]
    POST_ID --> POST_DELETE["DELETE"]

    POST_ID --> POST_COMMENTS["/comments"]
    POST_COMMENTS --> COMMENTS_GET["GET"]
    POST_COMMENTS --> COMMENTS_POST["POST"]

    POST_ID --> POST_TAGS["/tags"]
    POST_TAGS --> TAGS_GET["GET"]
    POST_TAGS --> TAGS_POST["POST"]

    %% COMMENTS
    COMMENTS --> COMMENT_ID["/comments/{comment_id}"]
    COMMENT_ID --> COMMENT_GET["GET"]
    COMMENT_ID --> COMMENT_PUT["PUT"]
    COMMENT_ID --> COMMENT_PATCH["PATCH"]
    COMMENT_ID --> COMMENT_DELETE["DELETE"]

    %% TAGS
    TAGS --> TAGS_LIST["GET /tags"]
    TAGS --> TAGS_CREATE["POST /tags"]
    TAGS --> TAG_ID["/tags/{tag_id}"]

    TAG_ID --> TAG_GET["GET"]
    TAG_ID --> TAG_PUT["PUT"]
    TAG_ID --> TAG_PATCH["PATCH"]
    TAG_ID --> TAG_DELETE["DELETE"]