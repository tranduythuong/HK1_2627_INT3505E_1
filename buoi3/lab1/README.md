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

    API --> USERS["Users"]
    API --> POSTS["Posts"]
    API --> COMMENTS["Comments"]
    API --> TAGS["Tags"]
    API --> PROFILES["Profiles"]
    API --> FOLLOWS["Follows"]

    USERS --> PROFILES
    USERS --> POSTS
    USERS --> FOLLOWS
    FOLLOWS --> USERS

    POSTS --> COMMENTS
    POSTS --> TAGS