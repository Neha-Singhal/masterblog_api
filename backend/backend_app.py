from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
    {"id": 3, "title": "Third post", "content": "This is the third post."},

    
]

#GET : Fetch all blog post
@app.route('/api/posts', methods=['GET'])
def get_posts():
    return jsonify(POSTS)

#PoST: Add new blog post
@app.route('/api/posts',methods=['POST'])
def add_post():
    data = request.get_json

    #Error Handling: Check if 'title' and 'content' are provided
    if not data or 'title' not in data or 'content' not in data:
        return jsonify({"error":"Both 'title' and 'content' are required"}), 400

    #Generate unique id for new post
    new_id = max(post["id"] for post in POSTS) + 1 if POSTS else 1

    #Create the new post
    new_post = {
        "id" : new_id,
        "title": data["title"],
        "content": data["content"]
    }

    POSTS.append(new_post)
    return jsonify(new_post), 201

#DELETE : delete a blog post by id
@app.route('/api/posts/<int:post_id>',methods=['DELETE'])
def delete_post(post_id):
    global POSTS
    post_to_delete = next((post for post in POSTS if post["id"] == post_id), None)

    # If the post is not found, return 404 Not Found
    if not post_to_delete:
        return jsonify({"error": f"post with id {post_id}  not found"})

    #Remove the post from list
    POSTS = [post for post in POSTS if post["id"] != post_id]
    return jsonify({"message": f"post with id {post_id} has been deleted sucessfully."})

#PUT :Update a blog post by ID
@app.route('/api/posts/<int:post_id>',methods=['PUT'])
def update_post(post_id):
    data = request.get_json()

    post = next((post for post in POSTS if post["id"] == post_id), None)
    if not post:
        return jsonify({"error": f"post with id {post_id}  not found"}), 404

    #Update the title and content if provided
    post["title"] = data.get("title" , post["title"])
    post ["content"] = data.get ("content", post["content"])
    return jsonify(post),200







if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
